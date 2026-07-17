from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

from app.database.connection import get_db
from app.main import app
from app.models.base import Base

TEST_DB_URL = "sqlite://"


@pytest.fixture
def db_session():
    engine = create_engine(
        TEST_DB_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    from sqlalchemy.orm import sessionmaker

    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def token(client):
    resp = client.post(
        "/auth/register",
        json={"email": "admin@test.com", "password": "test123", "role": "admin"},
    )
    assert resp.status_code == 201
    resp = client.post(
        "/auth/token",
        json={"email": "admin@test.com", "password": "test123"},
    )
    assert resp.status_code == 200
    return resp.json()["access_token"]


def auth_headers(token: str):
    return {"Authorization": f"Bearer {token}"}


class TestAuth:
    def test_register_and_login(self, client):
        resp = client.post(
            "/auth/register",
            json={"email": "user@test.com", "password": "pass123", "role": "operator"},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["email"] == "user@test.com"
        assert "id" in data

        resp = client.post(
            "/auth/token",
            json={"email": "user@test.com", "password": "pass123"},
        )
        assert resp.status_code == 200
        assert "access_token" in resp.json()

    def test_register_duplicate_email(self, client):
        client.post(
            "/auth/register",
            json={"email": "dup@test.com", "password": "pass123"},
        )
        resp = client.post(
            "/auth/register",
            json={"email": "dup@test.com", "password": "pass123"},
        )
        assert resp.status_code == 409

    def test_login_invalid_credentials(self, client):
        resp = client.post(
            "/auth/token",
            json={"email": "nonexist@test.com", "password": "wrong"},
        )
        assert resp.status_code == 401

    def test_missing_token_returns_401(self, client):
        resp = client.get("/operators")
        assert resp.status_code == 401

    def test_invalid_token_returns_401(self, client):
        resp = client.get("/operators", headers={"Authorization": "Bearer invalid"})
        assert resp.status_code == 401

    def test_valid_token_succeeds(self, client, token):
        resp = client.get("/operators", headers=auth_headers(token))
        assert resp.status_code == 200


class TestHealth:
    def test_health_public(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert "database" in data

    def test_health_no_auth_required(self, client):
        resp = client.get("/health", headers={})
        assert resp.status_code == 200


class TestOperators:
    def test_create_operator(self, client, token):
        resp = client.post(
            "/operators",
            headers=auth_headers(token),
            json={"name": "John", "department": "IT", "position": "Technician"},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "John"

    def test_list_operators(self, client, token):
        client.post(
            "/operators",
            headers=auth_headers(token),
            json={"name": "John", "department": "IT", "position": "Technician"},
        )
        resp = client.get("/operators", headers=auth_headers(token))
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_get_operator_not_found(self, client, token):
        resp = client.get("/operators/999", headers=auth_headers(token))
        assert resp.status_code == 404

    def test_delete_operator_not_found(self, client, token):
        resp = client.delete("/operators/999", headers=auth_headers(token))
        assert resp.status_code == 404

    def test_read_operator_with_id_0(self, client, token):
        resp = client.get("/operators/0", headers=auth_headers(token))
        assert resp.status_code == 422


class TestEquipment:
    def test_create_specs_then_equipment(self, client, token):
        spec_resp = client.post(
            "/specs",
            headers=auth_headers(token),
            json={
                "cpu": {"brand": "Intel", "model": "i7"},
                "ram": {"capacity": {"value": 16, "unit": "GB"}, "mode": "dual"},
                "storage": {"capacity": {"value": 512, "unit": "GB"}, "type": "SSD"},
                "graphics": {
                    "brand": "NVIDIA",
                    "model": "RTX 3060",
                    "type": "dedicated",
                    "memory": {"value": 12, "unit": "GB"},
                },
            },
        )
        assert spec_resp.status_code == 201
        spec_id = spec_resp.json()["id"]

        resp = client.post(
            "/equipment",
            headers=auth_headers(token),
            json={
                "serial": "SN-001",
                "brand": "Dell",
                "model": "XPS 15",
                "specs_id": spec_id,
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["serial"] == "SN-001"

    def test_create_equipment_missing_specs(self, client, token):
        resp = client.post(
            "/equipment",
            headers=auth_headers(token),
            json={"serial": "SN-002", "brand": "Dell", "model": "XPS", "specs_id": 999},
        )
        assert resp.status_code == 404


class TestAssignments:
    def test_full_assignment_flow(self, client, token):
        op_resp = client.post(
            "/operators",
            headers=auth_headers(token),
            json={"name": "Alice", "department": "IT", "position": "Tech"},
        )
        op_id = op_resp.json()["id"]

        spec_resp = client.post(
            "/specs",
            headers=auth_headers(token),
            json={
                "cpu": {"brand": "Intel", "model": "i5"},
                "ram": {"capacity": {"value": 8, "unit": "GB"}, "mode": "single"},
                "storage": {"capacity": {"value": 256, "unit": "GB"}, "type": "SSD"},
                "graphics": {
                    "brand": "Intel",
                    "model": "UHD",
                    "type": "integrated",
                    "memory": None,
                },
            },
        )
        spec_id = spec_resp.json()["id"]

        eq_resp = client.post(
            "/equipment",
            headers=auth_headers(token),
            json={
                "serial": "SN-010",
                "brand": "Lenovo",
                "model": "ThinkPad",
                "specs_id": spec_id,
            },
        )
        eq_id = eq_resp.json()["id"]

        assign_resp = client.post(
            "/assignments",
            headers=auth_headers(token),
            json={
                "equipment_id": eq_id,
                "operator_id": op_id,
                "assigned_by": op_id,
            },
        )
        assert assign_resp.status_code == 201

        dup_resp = client.post(
            "/assignments",
            headers=auth_headers(token),
            json={
                "equipment_id": eq_id,
                "operator_id": op_id,
                "assigned_by": op_id,
            },
        )
        assert dup_resp.status_code == 409


class TestHistory:
    def test_history_immutable_delete(self, client, token):
        op_resp = client.post(
            "/operators",
            headers=auth_headers(token),
            json={"name": "Bob", "department": "IT", "position": "Tech"},
        )
        op_id = op_resp.json()["id"]

        spec_resp = client.post(
            "/specs",
            headers=auth_headers(token),
            json={
                "cpu": {"brand": "Intel", "model": "i5"},
                "ram": {"capacity": {"value": 8, "unit": "GB"}, "mode": "single"},
                "storage": {"capacity": {"value": 256, "unit": "GB"}, "type": "SSD"},
                "graphics": {
                    "brand": "Intel",
                    "model": "UHD",
                    "type": "integrated",
                    "memory": None,
                },
            },
        )
        spec_id = spec_resp.json()["id"]

        eq_resp = client.post(
            "/equipment",
            headers=auth_headers(token),
            json={
                "serial": "SN-100",
                "brand": "HP",
                "model": "ProBook",
                "specs_id": spec_id,
            },
        )
        eq_id = eq_resp.json()["id"]

        hist_resp = client.post(
            "/history",
            headers=auth_headers(token),
            json={
                "equipment_id": eq_id,
                "type": "repair",
                "reason": "Broken screen",
                "reported_by": op_id,
                "technician_id": op_id,
            },
        )
        assert hist_resp.status_code == 201
        hist_id = hist_resp.json()["id"]

        delete_resp = client.delete(f"/history/{hist_id}", headers=auth_headers(token))
        assert delete_resp.status_code == 403
