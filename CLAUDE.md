# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## 🏗️ Project Overview

**Gustos y Sabores** — Restaurant management platform (MVP 1). Headless architecture with Django REST backend, Astro frontend, MySQL persistence, and Docker-based local development.

Stack:
- **Backend**: Django 4.2, Django REST Framework 3.14, MySQL 8.4 (SQLite fallback)
- **Frontend**: Astro 6.1, TypeScript, Vanilla JS
- **Infra**: Docker Compose, Gunicorn, N+1 query optimization

Architecture: **Screaming Architecture** pattern. Django apps organized by domain (menu, orders, reservations, users, common, etc.). No traditional "models/views/serializers" folders—each app groups its own models, views, serializers, and tests.

---

## 📋 Development Commands

### Backend

```bash
# Setup
python -m venv .venv && source .venv/bin/activate
pip install -r backend/requirements/base.txt

# Database
python backend/manage.py migrate                    # Run migrations
python backend/manage.py seed_mvp                  # Load demo data (dishes, orders, reservations)

# Running
python backend/manage.py runserver                 # Dev server (port 8000)
python backend/manage.py check                     # Django static checks

# Testing
python backend/manage.py test apps.common apps.menu apps.orders apps.reservations apps.users
python backend/manage.py test apps.orders.tests.test_views --verbosity=2  # Single test module
```

### Frontend

```bash
# Setup
cd frontend && npm install

# Running
npm run dev         # Dev server (port 4321, hot reload)
npm run build       # Production build
npm run preview     # Preview build
```

### Docker (All-in-One)

```bash
docker compose -f infra/compose/docker-compose.yml up --build     # Start everything
docker compose -f infra/compose/docker-compose.yml down           # Stop everything
```

Services available locally:
- Frontend: `http://localhost:4321`
- Backend API: `http://localhost:8000/api`
- Django Admin: `http://localhost:8000/admin`

---

## 🗂️ Codebase Structure

```
backend/
├── apps/
│   ├── common/          # TimeStampedModel, DashboardKPIView
│   ├── users/           # Auth (tokens), roles, User model
│   ├── menu/            # Categories, Dishes, seed_mvp command
│   ├── orders/          # Orders, OrderItems (atomic tx pattern)
│   ├── reservations/    # Reservations, validation, party_size constraints
│   ├── billing/         # [Billing domain]
│   ├── inventory/       # [Inventory domain]
│   ├── promotions/      # [Promotions domain]
│   └── suppliers/       # [Suppliers domain]
├── config/              # Django settings (settings.py)
├── manage.py            # Django CLI
└── requirements/        # base.txt (dependencies)

frontend/
├── src/
│   ├── pages/           # File-based routing (index, menu, pedidos, reservas, login, dashboard)
│   ├── layouts/         # Layout.astro (base HTML template)
│   ├── components/      # Reusable UI components
│   └── assets/          # CSS, images
└── package.json
```

---

## 🛡️ Key Architectural Patterns

### 1. **Atomic Transactions in Orders**
Order creation wraps DB operations in `transaction.atomic()` to prevent partial writes. See `apps/orders/serializers.py: create()`.

**Why**: Consistency. Prevents: header persisted but items fail, or vice versa.

### 2. **N+1 Query Optimization**
Menu listing uses `select_related("category")` and `prefetch_related` with `Prefetch` objects to batch load categories and dishes in a single query.

**Why**: Performance. Cold loads ~50 dishes + categories = 2 queries, not 51.

### 3. **TimeStampedModel Base Class**
All models inherit `apps/common/models.py:TimeStampedModel` for `created_at` and `updated_at` fields.

**Why**: Audit trail. Every record knows when it was created and modified.

### 4. **Token Authentication**
Django REST Token auth. Clients send `Authorization: Token <key>` header. Public endpoints (register, menu, create order) allow anonymous; protected endpoints (customer history, admin KPIs) require token.

**Why**: Scalability. Stateless, no session storage. Admin dashboard auto-checks `IsStaffOrAdmin` permission.

### 5. **Screaming Architecture**
Folder structure reflects business domains, not technical layers. Each Django app self-contains its models, views, serializers, and tests. Not `/models`, `/views`, `/serializers` at project root.

**Why**: Clarity. Navigate `orders/` → understand order logic end-to-end. No `/models/order.py` scattered elsewhere.

---

## 📊 Database Schema Highlights

**Critical Constraints**:
- `menu_dish.price >= 0` (CHECK constraint)
- `orders_orderitem.quantity > 0` (CHECK constraint)
- `reservations_reservation.party_size > 0` (CHECK constraint)
- `orders_orderitem.dish` uses `ON DELETE PROTECT` — prevents deleting dishes with historical orders. Preserves accounting.
- `menu_category.name` and `menu_dish.name` are UNIQUE per category (composite unique constraint).

**No Direct Foreign Key Cycles**. User → Orders/Reservations; Dish → OrderItems (via FK, protected). Linear DAG.

---

## 🧪 Testing

Test files live **inside each app** (not a separate `/tests` dir).

```bash
# Run all tests
python backend/manage.py test apps.common apps.menu apps.orders apps.reservations apps.users

# Run one app
python backend/manage.py test apps.orders

# Run one test class
python backend/manage.py test apps.orders.tests.TestOrderCreation

# Run one test method
python backend/manage.py test apps.orders.tests.TestOrderCreation.test_atomic_transaction

# With verbose output
python backend/manage.py test apps.orders --verbosity=2
```

**Test Patterns**:
- Use `django.test.TransactionTestCase` if testing transaction behavior.
- Use `django.test.TestCase` otherwise (auto-rollback per test).
- Mock external APIs; keep DB tests real (integration tests).
- Fixtures: load data via `apps/menu/management/commands/seed_mvp.py` or `TestCase.fixtures = [...]`.

---

## 🔌 API Endpoints Quick Reference

**Public (AllowAny)**:
- `POST /api/auth/register/` — create account, return token
- `POST /api/auth/login/` — authenticate, return token
- `GET /api/menu/categories/` — list categories + dishes
- `GET /api/menu/dishes/` — list dishes, filter by `?category=<slug>`
- `POST /api/orders/` — create order (anon or authenticated)
- `POST /api/reservations/` — create reservation

**Authenticated (IsAuthenticated)**:
- `GET /api/auth/me/` — current user profile
- `GET /api/orders/` — user's order history
- `GET /api/reservations/` — user's reservation history

**Admin Only (IsStaffOrAdmin)**:
- `GET /api/dashboard/kpis/` — KPI metrics (admin view)

**Health**:
- `GET /api/health/` — DB + service status

---

## ⚡ Frontend (Astro)

**File-based Routing**:
- `pages/index.astro` → `/`
- `pages/menu.astro` → `/menu`
- `pages/pedidos.astro` → `/pedidos`
- `pages/reservas.astro` → `/reservas`
- `pages/login.astro` → `/login`
- `pages/dashboard.astro` → `/dashboard` (authenticated)

**Cart Management**:
- Vanilla JS (no Redux/Zustand).
- Stored in localStorage under key `'gustos_cart'`.
- Synced on page load; persists across sessions.
- Prices calculated server-side at order confirmation (no client-side price manipulation).

**Layout Template**:
- `layouts/Layout.astro` — base HTML, navigation, CSS variables for design system.

---

## 🚀 Environment & Configuration

**Local Dev (.env)**:
```bash
cp .env.example .env
# Edit for local MySQL or SQLite
# KEY env vars: DATABASE_URL, SECRET_KEY, DEBUG, ALLOWED_HOSTS
```

**Docker**:
- `docker-compose.yml` auto-generates env vars for services.
- MySQL container persists data to `mysql_data` volume.
- Backend waits for MySQL healthcheck before starting.

**Migrations**:
- Auto-generated by Django. New model? → `python backend/manage.py makemigrations` → `python backend/manage.py migrate`.
- Keep migrations committed; never edit by hand.

---

## 🔄 Common Workflows

### Add a New Endpoint

1. Define model in `apps/<domain>/models.py` (inherit `TimeStampedModel`).
2. Create serializer in `apps/<domain>/serializers.py`.
3. Create view in `apps/<domain>/views.py` (inherit `generics.ListAPIView`, etc.).
4. Register in `apps/<domain>/urls.py` (if exists) or `backend/config/urls.py`.
5. Run tests: `python backend/manage.py test apps.<domain>`.
6. Verify: `curl http://localhost:8000/api/<endpoint>/`.

### Add a New Frontend Page

1. Create `frontend/src/pages/<page>.astro`.
2. Import `Layout` from `layouts/Layout.astro`.
3. Wrap page content in `<Layout>` component.
4. Fetch data from backend API using `fetch()` in component or server-side via Astro `import`.
5. Hot reload on save: `npm run dev` watches for changes.

### Debug Order Creation

1. Break in `apps/orders/serializers.py:OrderCreateSerializer.create()`.
2. Check transaction is atomic: `with transaction.atomic():`.
3. Verify all OrderItems persisted: query `OrderItem.objects.filter(order_id=X)`.
4. Check dish prices captured at sale time (not live): `unit_price` field.
5. Validate totals: sum OrderItems by quantity × unit_price.

### Migrate from SQLite to MySQL

1. Dump SQLite: `python backend/manage.py dumpdata > backup.json`.
2. Point `DATABASE_URL` to MySQL.
3. Run migrations: `python backend/manage.py migrate`.
4. Load data: `python backend/manage.py loaddata backup.json`.
5. Or seed from scratch: `python backend/manage.py seed_mvp`.

---

## 📝 Code Standards

- **Naming**: Screaming Architecture. App name = domain. Model names = singular (User, Order, Dish). Serializers end in `Serializer`. Views end in `View`. Commands in `management/commands/`.
- **Imports**: Use absolute imports from project root (`from apps.orders.models import Order`, not relative `from ..models`).
- **Models**: Always inherit `TimeStampedModel`. Use `db_index=True` for frequently queried fields. Use `unique_together` or `UniqueConstraint` for composite keys.
- **Serializers**: Validate in `Meta.validators` or override `validate_<field>()`. Use `transaction.atomic()` in `create()`/`update()` for multi-table operations.
- **Views**: Use DRF generics. Override `get_queryset()` to apply filters/permissions. Use `select_related()` and `prefetch_related()` to avoid N+1.
- **Frontend**: Keep Astro pages simple. Extract logic to `src/components/`. Use vanilla JS for client interactivity; avoid heavy frameworks. Fetch from backend, never hardcode API URLs—use env vars.

---

## 🐛 Debugging

**Backend Logs**:
```bash
# Django debug toolbar
# Install: pip install django-debug-toolbar
# Add to INSTALLED_APPS and middleware in config/settings.py
# Visit http://localhost:8000 and click toolbar to inspect queries

# Manual logging
import logging
logger = logging.getLogger(__name__)
logger.debug(f"Order creation: {order_id}")
```

**Database Inspection**:
```bash
# SQLite (dev fallback)
sqlite3 backend/db.sqlite3
> SELECT * FROM orders_order LIMIT 5;

# MySQL (docker)
docker exec -it <mysql-container> mysql -u root -p<PASSWORD>
> USE gustos_db; SELECT * FROM orders_order LIMIT 5;
```

**Frontend**:
- Browser DevTools → Network → inspect API responses.
- LocalStorage → check `'gustos_cart'` JSON.
- Astro dev server logs appear in terminal.

---

## 🔐 Security Notes

- **No Client-Side Price Manipulation**: Prices are recalculated server-side from DB on order confirmation.
- **CORS**: Enabled for frontend origin (see `CORS_ALLOWED_ORIGINS` in settings).
- **Tokens**: Stored in `rest_framework.authtoken`. Never commit `.env` with real keys.
- **SQL Injection**: Django ORM parameterizes all queries; raw SQL is discouraged.
- **CSRF**: Disabled for API (token-based); enabled for admin panel.

---

## 📚 Related Documentation

- Main README: `/README.md` — architecture diagrams, ER model, endpoint catalog
- MVP Requirements: `/docs/mvp-1.md`
- Skill Registry: `/.atl/skill-registry.md` — team conventions and standards

---

## 🎯 Quick Checklist for New Contributors

- [ ] Clone repo, run `python -m venv .venv && source .venv/bin/activate && pip install -r backend/requirements/base.txt`
- [ ] Copy `.env.example` → `.env`, adjust DB settings
- [ ] `python backend/manage.py migrate && python backend/manage.py seed_mvp`
- [ ] `python backend/manage.py runserver` in one terminal
- [ ] `cd frontend && npm install && npm run dev` in another terminal
- [ ] Visit `http://localhost:4321` (frontend) and `http://localhost:8000/api` (backend)
- [ ] Run tests: `python backend/manage.py test apps.orders --verbosity=2`
- [ ] Read the main README for business context (domain, ER model)
