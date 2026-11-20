# EquipTracker — Sitio web

Sitio web del producto **EquipTracker**, el sistema de control de inventario
de TI: equipos, operadores, asignaciones e incidencias.

Este repositorio contiene únicamente la página de producto. El backend, el
cliente de escritorio y la demo se distribuyen en repositorios separados.

- Sitio: <https://equiptracker.rk8.dev>
- Demo: <https://demo.equiptracker.rk8.dev>
- Contacto: <equiptracker@rk8.dev>

## Tecnología

| Capa | Tecnología |
|---|---|
| Generación de sitio estático | Astro |
| Estilos | Tailwind CSS v4 |

## Desarrollo

```bash
pnpm install
pnpm dev      # servidor local
pnpm build    # genera dist/
pnpm preview  # sirve dist/
```

El contacto se hace por correo: no hay formulario ni endpoint. La página de
contacto muestra la dirección visible y permite copiarla.

## Imágenes

Las capturas en `public/placeholder-captura-*.svg` son provisionales: muestran
con texto qué imagen real debe ir en ese lugar. Sustitúyelas por capturas
reales conservando el mismo nombre de archivo o actualizando las referencias
en `src/pages/`.

## Marca y licencia

La marca, los colores y el diseño son propiedad de RK8; consulta `ASSETS.md`.
El código se distribuye bajo PolyForm Strict 1.0.0 (`LICENSE`). Las
dependencias de terceros se detallan en `NOTICE`.

EquipTracker está desarrollado por RK8.

Última actualización: 20 de noviembre de 2026.
