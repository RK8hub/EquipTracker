from os import environ
from typing import NewType

from dotenv import load_dotenv

load_dotenv()

DatabaseURL = NewType("DatabaseURL", str)

SecretKey = NewType("SecretKey", str)

SECRET_KEY: SecretKey = SecretKey(environ["SECRET_KEY"])

DATABASE_URL: DatabaseURL = DatabaseURL(environ["DB_URL"])
