# Gustos y Sabores

Base MVP 1 para el sistema web de gestion de pedidos y reservas del restaurante Gustos y Sabores.

## Stack

- `frontend/`: Astro + TypeScript
- `backend/`: Django + Django REST Framework
- `infra/`: Docker Compose
- `database`: MySQL 8

## Modulos MVP

- autenticacion basica por token
- menu y categorias
- creacion de pedidos
- creacion de reservas
- panel administrativo con Django Admin

## Estructura

```text
frontend/    Web publica MVP
backend/     API y panel administrativo
infra/       Dockerfiles y compose
docs/        Documentacion de producto y arquitectura
```

## Levantar con Docker

1. Copia `.env.example` a `.env` si quieres ajustar valores.
2. Ejecuta:

```bash
docker compose -f infra/compose/docker-compose.yml up --build
```

Servicios:

- Frontend: `http://localhost:4321`
- Backend API: `http://localhost:8000/api`
- Django Admin: `http://localhost:8000/admin`
- MySQL: `localhost:3306`

## Desarrollo local sin Docker

### Backend

```bash
./.venv/bin/pip install -r backend/requirements/base.txt
./.venv/bin/python backend/manage.py migrate
./.venv/bin/python backend/manage.py seed_mvp
./.venv/bin/python backend/manage.py runserver
```

Si no configuras MySQL, el backend usa SQLite como fallback local.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Usuario administrador

Crea uno con:

```bash
./.venv/bin/python backend/manage.py createsuperuser
```
