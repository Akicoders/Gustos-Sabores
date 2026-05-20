# Gustos y Sabores - Plataforma de Gestión de Pedidos y Reservas

Bienvenido a la documentación técnica oficial de **Gustos y Sabores**, un sistema moderno de gestión de reservas, pedidos y administración interna diseñado para optimizar las operaciones de nuestro restaurante. 

Este proyecto está construido bajo una arquitectura desacoplada que prioriza el rendimiento, la consistencia de los datos y una experiencia de usuario sumamente fluida.

---

## 🏗️ Arquitectura General del Sistema

El sistema implementa una arquitectura desacoplada (decapitada / headless) dividida en tres capas principales:

```text
 ┌─────────────────────────────────────────────────────────────┐
 │                Frontend (Astro + TypeScript)                │
 │       • Renderizado de Páginas Públicas y Clientes         │
 │       • Gestión reactiva del Carrito en LocalStorage        │
 └──────────────────────────────┬──────────────────────────────┘
                                │
                        Peticiones HTTP (REST API)
                                │
 ┌──────────────────────────────▼──────────────────────────────┐
 │             Backend API (Django + DRF)                      │
 │       • Arquitectura Modular Gritona (Screaming Apps)       │
 │       • Lógica de Negocio y Transacciones Atómicas          │
 └──────────────────────────────┬──────────────────────────────┘
                                │
                        Conexión TCP (3306)
                                │
 ┌──────────────────────────────▼──────────────────────────────┐
 │                  Base de Datos (MySQL 8.4)                  │
 │       • Restricciones de Integridad y Check Constraints      │
 └─────────────────────────────────────────────────────────────┘
```

### Flujo de Datos Típico
1. **Consulta del Menú**: El frontend realiza un `GET` a `/api/menu/dishes/`. El backend ejecuta un `prefetch_related` para traer los platos y categorías optimizando las queries y retorna el JSON. El cliente renderiza dinámicamente y expone los platos al usuario.
2. **Creación de Pedido**: El usuario acumula platos en su carrito local. Al confirmar, el frontend envía un `POST` a `/api/orders/`. El backend inicia una **transacción atómica**, valida la disponibilidad de los platos, calcula el precio total basado en los precios vigentes en la BD (evitando manipulaciones del lado del cliente) y persiste la información.

---

## 🗄️ Modelo de Base de Datos y Persistencia

El diseño de la base de datos se rige bajo la tercera forma normal (3NF) para evitar redundancias, asegurando la máxima consistencia e integridad referencial en escenarios de alta concurrencia.

### 📊 Diagrama Entidad-Relación Lógico

```text
  ┌─────────────────┐             ┌─────────────────┐
  │   users_user    │1           *│   reservation   │
  │  (Clientes/Adm) ├────────────►│  (Reservas)     │
  └────────┬────────┘             └─────────────────┘
           │1
           │
           │*
  ┌────────▼────────┐             ┌─────────────────┐
  │   orders_order  │1           *│  orders_item    │
  │  (Cabecera Ped) ├────────────►│  (Detalle Ped)  │
  └─────────────────┘             └────────┬────────┘
                                           │*
                                           │
                                           │1 (PROTECT)
  ┌─────────────────┐1           *┌────────▼────────┐
  │  menu_category  ├────────────►│    menu_dish    │
  │  (Categorías)   │             │   (Platos)      │
  └─────────────────┘             └─────────────────┘
```

---

### 📝 Diccionario de Datos Detallado

A continuación se detallan las tablas autogeneradas por las migraciones de Django en la base de datos MySQL:

#### 1. Auditoría Base (`TimeStampedModel`)
Una clase abstracta heredada por la mayoría de las tablas para asegurar un registro preciso de tiempos de creación y modificación:
- `created_at` (`datetime`): Fecha y hora de creación del registro (`auto_now_add=True`).
- `updated_at` (`datetime`): Fecha y hora de la última actualización (`auto_now=True`).

#### 2. Tabla: `users_user` (Usuarios del sistema)
Extiende el modelo `AbstractUser` de Django para permitir diferentes roles dentro de la plataforma.

| Campo | Tipo SQL | Restricciones | Descripción |
| :--- | :--- | :--- | :--- |
| `id` | `bigint` | `PRIMARY KEY`, `AUTO_INCREMENT` | Identificador único del usuario. |
| `username` | `varchar(150)` | `UNIQUE`, `NOT NULL` | Nombre de usuario para login. |
| `email` | `varchar(254)` | `UNIQUE`, `NOT NULL` | Correo electrónico institucional o de cliente. |
| `full_name` | `varchar(255)` | `NOT NULL` | Nombre completo del usuario. |
| `phone` | `varchar(30)` | `NULL` | Teléfono de contacto. |
| `address` | `varchar(255)` | `NULL` | Dirección por defecto para entregas. |
| `role` | `varchar(20)` | `NOT NULL`, `DEFAULT 'customer'` | Roles: `'customer'` (Cliente), `'staff'` (Personal), `'admin'` (Administrador). |

#### 3. Tabla: `menu_category` (Categorías del menú)

| Campo | Tipo SQL | Restricciones | Descripción |
| :--- | :--- | :--- | :--- |
| `id` | `bigint` | `PRIMARY KEY`, `AUTO_INCREMENT` | Identificador único de la categoría. |
| `name` | `varchar(120)` | `UNIQUE`, `NOT NULL` | Ejemplo: "Entradas", "Segundos", "Bebidas". |
| `slug` | `varchar(140)` | `UNIQUE`, `NOT NULL` | Representación amigable para URLs (ej: `entradas`). |

#### 4. Tabla: `menu_dish` (Platos individuales)

| Campo | Tipo SQL | Restricciones | Descripción |
| :--- | :--- | :--- | :--- |
| `id` | `bigint` | `PRIMARY KEY`, `AUTO_INCREMENT` | Identificador único del plato. |
| `category_id` | `bigint` | `FOREIGN KEY` -> `menu_category.id` | Categoría asociada (`ON DELETE CASCADE`). |
| `name` | `varchar(140)` | `NOT NULL` | Nombre del plato (ej: "Lomo Saltado"). |
| `slug` | `varchar(160)` | `UNIQUE`, `NOT NULL` | Slug único para consultas optimizadas. |
| `description` | `longtext` | `NULL` | Ingredientes, alérgenos y descripción comercial. |
| `price` | `decimal(10,2)` | `NOT NULL` | Precio de venta. Constraint: `price >= 0`. |
| `is_available` | `tinyint(1)` | `NOT NULL`, `DEFAULT 1` | Si está disponible para la venta en el día. |
| `image_url` | `varchar(200)` | `NULL` | URL de la imagen del plato. |

> [!IMPORTANT]
> **Constraint de Unicidad**: Existe una restricción única compuesta (`UniqueConstraint`) en los campos `(category_id, name)` que impide registrar platos duplicados con el mismo nombre dentro de una misma categoría.

#### 5. Tabla: `orders_order` (Cabecera del Pedido)

| Campo | Tipo SQL | Restricciones | Descripción |
| :--- | :--- | :--- | :--- |
| `id` | `bigint` | `PRIMARY KEY`, `AUTO_INCREMENT` | Identificador único del pedido. |
| `user_id` | `bigint` | `FOREIGN KEY` -> `users_user.id`, `NULL` | Usuario registrado que hace el pedido (`ON DELETE SET_NULL`). |
| `customer_name` | `varchar(255)` | `NOT NULL` | Nombre de contacto para el pedido. |
| `customer_email` | `varchar(254)` | `NOT NULL` | Correo de confirmación. |
| `customer_phone` | `varchar(30)` | `NOT NULL` | Teléfono de coordinación. |
| `delivery_address` | `varchar(255)` | `NULL` | Dirección de entrega (obligatoria si `order_type == 'delivery'`). |
| `order_type` | `varchar(20)` | `NOT NULL`, `DEFAULT 'local'` | Tipo de consumo: `'local'` o `'delivery'`. |
| `payment_method` | `varchar(20)` | `NOT NULL`, `DEFAULT 'cash'` | Métodos: `'cash'` (Contra entrega), `'yape'`, o `'card'` (Tarjeta). |
| `status` | `varchar(20)` | `NOT NULL`, `DEFAULT 'pending'` | Estados: `'pending'`, `'preparing'`, `'ready'`, `'delivered'`, `'cancelled'`. |
| `notes` | `longtext` | `NULL` | Especificaciones (ej: "Sin cebolla"). |
| `total` | `decimal(10,2)` | `NOT NULL`, `DEFAULT 0.00` | Monto total calculado del pedido. |

#### 6. Tabla: `orders_orderitem` (Detalle o Líneas de Pedido)

| Campo | Tipo SQL | Restricciones | Descripción |
| :--- | :--- | :--- | :--- |
| `id` | `bigint` | `PRIMARY KEY`, `AUTO_INCREMENT` | Identificador único de la línea de detalle. |
| `order_id` | `bigint` | `FOREIGN KEY` -> `orders_order.id` | Cabecera del pedido asociada (`ON DELETE CASCADE`). |
| `dish_id` | `bigint` | `FOREIGN KEY` -> `menu_dish.id` | Plato solicitado. Restricción: **`ON DELETE PROTECT`**. |
| `quantity` | `int unsigned` | `NOT NULL` | Cantidad del plato. Constraint: `quantity > 0`. |
| `unit_price` | `decimal(10,2)` | `NOT NULL` | Precio histórico capturado al momento de la venta. |

> [!CAUTION]
> **Integridad Referencial Crítica**: La relación `dish` utiliza `on_delete=models.PROTECT`. Esto significa que ningún administrador podrá borrar un plato de la base de datos si este ya forma parte de un pedido existente, protegiendo la consistencia de los reportes históricos de venta y la contabilidad.

#### 7. Tabla: `reservations_reservation` (Gestión de Reservas de Mesas)

| Campo | Tipo SQL | Restricciones | Descripción |
| :--- | :--- | :--- | :--- |
| `id` | `bigint` | `PRIMARY KEY`, `AUTO_INCREMENT` | Identificador de la reserva. |
| `user_id` | `bigint` | `FOREIGN KEY` -> `users_user.id`, `NULL` | Usuario registrado que reserva (`ON DELETE SET_NULL`). |
| `customer_name` | `varchar(255)` | `NOT NULL` | Nombre del titular de la reserva. |
| `customer_email` | `varchar(254)` | `NOT NULL` | Correo de contacto. |
| `customer_phone` | `varchar(30)` | `NOT NULL` | Teléfono para reconfirmar la mesa. |
| `reserved_at` | `datetime` | `NOT NULL` | Fecha y hora reservada. |
| `party_size` | `int unsigned` | `NOT NULL` | Cantidad de personas. Constraint: `party_size > 0`. |
| `status` | `varchar(20)` | `NOT NULL`, `DEFAULT 'pending'` | Estados: `'pending'`, `'confirmed'`, `'cancelled'`. |
| `notes` | `longtext` | `NULL` | Detalles especiales (ej: "Mesa cerca de la ventana"). |

---

## ⚙️ Backend: Django REST Framework (API & Admin)

El backend actúa como una API REST pura y un panel administrativo integrado. Está construido bajo principios SOLID y una **Screaming Architecture**, donde la estructura de carpetas grita de forma explícita el negocio del restaurante.

### 📂 Estructura de Módulos (Apps)
Dentro del directorio `backend/apps/`:
- `common/`: Contiene el modelo base `TimeStampedModel` y la vista analítica del Dashboard para el administrador (`DashboardKPIView`).
- `users/`: Gestión de usuarios, roles, perfiles y autenticación basada en tokens.
- `menu/`: Administración de categorías y platos del restaurante.
- `orders/`: Gestión del flujo completo de pedidos e items de venta.
- `reservations/`: Control de reserva de mesas y validación de aforos.

---

### 🛡️ Autenticación y Permisos
El sistema implementa una **Autenticación por Token** (`rest_framework.authtoken`).
- **Público**: Registro de usuarios, login, consulta de platos del menú y creación de pedidos o reservas (anonimato permitido).
- **Protegido (Cliente)**: Los clientes autenticados pueden acceder a su propio historial enviando el header:
  `Authorization: Token <clave_token>`
- **Protegido (Staff / Admin)**: Las vistas analíticas avanzadas (KPIs) y el panel administrativo requieren permisos específicos (`IsStaffOrAdmin`).

---

### 📋 Catálogo Completo de Endpoints REST API

| Método | Endpoint | Permiso Requerido | Descripción | Parámetros / Payload clave |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/api/health/` | `AllowAny` | Check de salud del backend y base de datos. | Ninguno. |
| `POST` | `/api/auth/register/` | `AllowAny` | Registra un nuevo cliente y genera su token. | `username`, `email`, `password`, `full_name` |
| `POST` | `/api/auth/login/` | `AllowAny` | Autentica un usuario y retorna su token. | `username`, `password` |
| `GET` | `/api/auth/me/` | `IsAuthenticated` | Obtiene los detalles del perfil actual. | Requiere Token. |
| `GET` | `/api/menu/categories/` | `AllowAny` | Obtiene categorías agrupando sus platos activos. | Ninguno. |
| `GET` | `/api/menu/dishes/` | `AllowAny` | Listado plano de platos disponibles. | QueryParam `?category=<slug>` para filtrar. |
| `POST` | `/api/orders/` | `AllowAny` | Registra un pedido en el sistema (anónimo o con user). | `customer_name`, `delivery_address`, `items` |
| `GET` | `/api/orders/` | `IsAuthenticated` | Listado histórico de pedidos del cliente logueado. | Requiere Token. |
| `POST` | `/api/reservations/` | `AllowAny` | Registra una solicitud de reserva de mesa. | `customer_name`, `reserved_at`, `party_size` |
| `GET` | `/api/reservations/` | `IsAuthenticated` | Listado de reservas del cliente logueado. | Requiere Token. |
| `GET` | `/api/dashboard/kpis/` | `IsStaffOrAdmin` | Dashboard KPI analítico para gerencia y personal. | Requiere Token de administrador/staff. |

---

### 🧠 Patrones de Código Destacados del Backend

#### 1. Transaccionalidad Atómica en Pedidos
Para evitar inconsistencias financieras catastróficas (por ejemplo, registrar una cabecera de pedido pero que falle el registro de sus platos asociados debido a un error de red o de BD), el backend encapsula la creación en una transacción atómica:

```python
# apps/orders/serializers.py
from django.db import transaction

def create(self, validated_data):
    with transaction.atomic():
        # Extracción y registro de datos
        # Cálculo dinámico del precio en servidor
        # Persistencia en bloque
```

#### 2. Evitando el Problema de N+1 Queries
Al listar los platos, en lugar de consultar la base de datos por cada plato para averiguar su categoría, Django realiza un **Join implícito** optimizado utilizando `select_related` y `prefetch_related`:

```python
# apps/menu/views.py
class CategoryListView(generics.ListAPIView):
    def get_queryset(self):
        available_dishes = Dish.objects.filter(is_available=True).select_related("category")
        return Category.objects.filter(dishes__is_available=True).distinct().prefetch_related(
            Prefetch("dishes", queryset=available_dishes)
        )
```

---

## 💻 Frontend: Astro + TypeScript (Web Pública)

El frontend de **Gustos y Sabores** está construido usando **Astro**, el moderno framework que prioriza la velocidad web reduciendo el Javascript del lado del cliente mediante la arquitectura de islas.

### 📁 Estructura del Frontend
Dentro de `frontend/src/`:
- `layouts/Layout.astro`: Plantilla base HTML5 que unifica la cabecera, navegación dinámica y pie de página, incluyendo el sistema de diseño visual (CSS variables).
- `pages/`: Cada archivo `.astro` equivale a una página web autogenerada (File-based Routing):
  - `index.astro`: Landing page de bienvenida con promociones destacadas.
  - `acerca.astro`: Historia del restaurante y propuesta gastronómica.
  - `menu.astro`: Catálogo dinámico conectado directamente a la API REST.
  - `pedidos.astro`: Formulario inteligente para registrar pedidos con carrito interactivo.
  - `reservas.astro`: Formulario con validaciones en tiempo real para reservar mesas.
  - `login.astro` y `dashboard.astro`: Autenticación de clientes y panel personalizado donde ven sus pedidos y reservas históricas en tiempo real.

---

### 🛒 Gestión del Carrito (Vanilla JS + LocalStorage Reactivo)
En lugar de forzar pesadas librerías de estado (como Redux o Zustand), la gestión del carrito se resuelve de forma eficiente con Vanilla JavaScript nativo y almacenamiento local:
- **Persistencia**: El carrito se almacena en el navegador bajo la key `'gustos_cart'`.
- **Sincronización**: Al ingresar a la página de `/pedidos`, el frontend recupera el arreglo JSON, autocompleta el formulario y calcula subtotales al instante sin requerir peticiones adicionales al servidor hasta la confirmación final.

---

## 🐳 Infraestructura y Despliegue Local (Docker Compose)

El proyecto incluye un entorno de desarrollo completamente automatizado y reproducible mediante contenedores de Docker.

### 🧱 Componentes de Infraestructura
El archivo `infra/compose/docker-compose.yml` define tres servicios comunicados en red privada:
1. **`mysql`**: Levanta una instancia de MySQL 8.4 sobre el puerto `3306` mapeado externamente, persistiendo datos de forma persistente en un volumen de Docker (`mysql_data`).
2. **`backend`**: Levanta la aplicación Django REST expuesta en el puerto `8000`. Espera a que el contenedor de base de datos responda afirmativamente mediante un `healthcheck` saludable antes de arrancar.
3. **`frontend`**: Levanta el servidor de Astro expuesto en el puerto `4321`. Se comunica bidireccionalmente con el backend mediante variables de entorno.

---

## 🚀 Guía de Inicio Rápido

### Requisitos Previos
- Docker y Docker Compose instalados en tu sistema.
- O en su defecto (desarrollo local sin Docker): Python >= 3.10, Node.js >= 22.12.0.

### Método 1: Levantar todo con Docker (Recomendado)
Tenés que ejecutar el siguiente comando desde la raíz del proyecto:

```bash
docker compose -f infra/compose/docker-compose.yml up --build
```

Una vez finalizado, los servicios estarán disponibles en:
- 🌐 **Frontend**: `http://localhost:4321`
- ⚙️ **Backend API**: `http://localhost:8000/api`
- 🛡️ **Django Admin**: `http://localhost:8000/admin`

---

### Método 2: Levantar de forma Local (Sin Docker)

#### 1. Configuración de Variables de Entorno
Copia el archivo `.env.example` a `.env` y editalo según tus preferencias locales:
```bash
cp .env.example .env
```
*Si no configuras un servidor de MySQL local, el backend usará automáticamente SQLite como base de datos de contingencia en desarrollo.*

#### 2. Inicializar el Backend
```bash
# Crear entorno virtual e instalar dependencias
python -m venv .venv
source .venv/bin/activate  # En Windows usa: .venv\Scripts\activate
pip install -r backend/requirements/base.txt

# Correr migraciones
python backend/manage.py migrate

# Opcional: Cargar datos demo de platos, categorías, pedidos y reservas
python backend/manage.py seed_mvp

# Levantar servidor
python backend/manage.py runserver
```

#### 3. Inicializar el Frontend
```bash
cd frontend
npm install
npm run dev
```

---

## 🧪 Pruebas y Calidad de Código

### Ejecución del Suite de Tests del Backend
El backend implementa un set robusto de pruebas unitarias y de integración que validan la lógica de los endpoints, serializadores y restricciones de modelos:

```bash
# Correr todas las pruebas unitarias
python backend/manage.py test apps.common apps.menu apps.orders apps.reservations apps.users

# Ejecutar el check estático de Django
python backend/manage.py check
```

---

## 👥 Equipo y Mantenimiento

Este proyecto ha sido optimizado con los más altos estándares de calidad arquitectónica (SOLID, Clean Code). Para dudas o contribuciones al MVP 1, comunícate con el administrador de infraestructura del restaurante.

¡Buen provecho con el desarrollo! 🍳
