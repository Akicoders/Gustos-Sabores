# Frontend Gustos y Sabores

Aplicacion publica Astro para el MVP de pedidos, reservas, menu y dashboard demo de Gustos y Sabores.

## Desarrollo

```bash
npm install
npm run dev
```

La API se configura con `PUBLIC_API_URL`; por defecto usa `http://localhost:8000/api`.

## Estructura

```text
src/layouts/Layout.astro   Layout global y estilos base
src/pages/                 Paginas publicas del MVP
public/                    Favicons y assets publicos
```

## Notas

- El dashboard publico muestra fallback demo si la API protegida de KPIs responde `401` o `403`.
- Las promociones son demo: agregan platos reales del menu con precio real de carta, no combos falsos enviados al backend.
