# Guía de Despliegue — Gustos y Sabores

## Introducción

Este documento proporciona una guía completa para desplegar la aplicación **Gustos y Sabores** a un entorno de producción. La aplicación utiliza una arquitectura moderna de microservicios con un backend Django REST y un frontend Astro, con infraestructura containerizada mediante Docker.

---

## 1. Arquitectura Tecnológica General

### 1.1 Stack Tecnológico

| Capa | Tecnología | Versión | Propósito |
|------|-----------|---------|----------|
| **Frontend** | Astro | 6.1.8 | Framework SSR/SSG para UI renderizada en servidor |
| **Frontend** | TypeScript | 5.9.3 | Type-safe client-side scripting |
| **Frontend** | Node.js | ≥22.12.0 | Runtime para build y desarrollo |
| **Backend** | Django | 4.2.x | Framework web y ORM |
| **Backend** | Django REST Framework | 3.14.x | API REST y serialización |
| **Backend** | Gunicorn | 21.x+ | WSGI application server |
| **Database** | MySQL | 8.4.x | Base de datos relacional principal |
| **Cache** | Redis | 7.x (opcional) | Cache distribuido y session store |
| **Containerización** | Docker | 24.x+ | Contenerización de servicios |
| **Orquestación** | Docker Compose | 2.x+ | Orquestación local y producción pequeña |
| **Reverse Proxy** | Nginx | 1.25+ | Proxy inverso y servidor estático |
| **Testing** | Vitest | 4.1.7 | Testing de frontend |
| **Testing** | pytest | - | Testing de backend (recomendado) |

### 1.2 Topología de Infraestructura

```
┌─────────────────────────────────────────────────┐
│         Nginx (Reverse Proxy, SSL/TLS)         │
│                  :443 / :80                     │
└──────────────────┬──────────────────────────────┘
                   │
        ┌──────────┴──────────┐
        │                     │
   ┌────▼────────┐     ┌──────▼──────────┐
   │ Frontend    │     │ Backend API     │
   │ (Astro)     │     │ (Django/DRF)    │
   │ :3000       │     │ :8000           │
   └─────────────┘     └────┬────────────┘
                             │
                    ┌────────▼─────────┐
                    │ MySQL Database   │
                    │ :3306            │
                    └──────────────────┘
```

---

## 2. Requisitos Previos de Infraestructura

### 2.1 Hardware Mínimo

Para un despliegue pequeño en producción:

- **CPU**: 2 cores (4 cores recomendado para escalabilidad)
- **RAM**: 4 GB (8 GB recomendado)
- **Disco**: 50 GB (SSD recomendado)
- **Ancho de banda**: 10 Mbps uplink (conexión estable)

### 2.2 Sistema Operativo

Entornos soportados:
- **Linux**: Ubuntu 22.04 LTS, Debian 12 (recomendado)
- **macOS**: 12.0+ (desarrollo/staging)
- **Windows**: WSL 2 con Ubuntu 22.04 (desarrollo)

### 2.3 Dependencias del Sistema

#### En Ubuntu/Debian:

```bash
sudo apt-get update
sudo apt-get install -y \
  curl \
  wget \
  git \
  build-essential \
  libssl-dev \
  libffi-dev \
  python3.11 \
  python3.11-venv \
  python3.11-dev \
  mysql-client \
  postgresql-client \
  docker.io \
  docker-compose \
  nginx \
  supervisor \
  certbot \
  python3-certbot-nginx
```

---

## 3. Preparación del Entorno de Producción

### 3.1 Variables de Entorno

Crear archivo `.env.production` en la raíz del proyecto:

```bash
# Django Configuration
DEBUG=False
SECRET_KEY=<generar con secrets.token_urlsafe(50)>
ALLOWED_HOSTS=example.com,www.example.com
CSRF_TRUSTED_ORIGINS=https://example.com,https://www.example.com

# Database
DATABASE_URL=mysql://gustos_user:strong_password_here@mysql:3306/gustos_db
DATABASE_ENGINE=django.db.backends.mysql
DATABASE_POOL_SIZE=20

# Cache (opcional)
CACHE_URL=redis://redis:6379/0

# Frontend
PUBLIC_API_URL=https://api.example.com/api
FRONTEND_URL=https://example.com

# CORS
CORS_ALLOWED_ORIGINS=https://example.com,https://www.example.com

# Security
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True

# Email (si se implementa)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-app-password

# Logging
LOG_LEVEL=INFO
```

### 3.2 Generación de Claves Secretas

```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## 4. Despliegue de Base de Datos

### 4.1 Instalación de MySQL 8.4

#### En Ubuntu/Debian:

```bash
# Instalación
sudo apt-get install mysql-server

# Asegurar la instalación
sudo mysql_secure_installation

# Iniciar servicio
sudo systemctl start mysql
sudo systemctl enable mysql
```

#### Con Docker (recomendado):

```bash
docker pull mysql:8.4
docker run -d \
  --name gustos-mysql \
  -e MYSQL_ROOT_PASSWORD=root_password \
  -e MYSQL_DATABASE=gustos_db \
  -e MYSQL_USER=gustos_user \
  -e MYSQL_PASSWORD=user_password \
  -v mysql_data:/var/lib/mysql \
  -p 3306:3306 \
  mysql:8.4
```

### 4.2 Configuración de Base de Datos

```bash
# Conectar a MySQL
mysql -u root -p

# Crear usuario y base de datos
CREATE DATABASE gustos_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'gustos_user'@'localhost' IDENTIFIED BY 'strong_password';
GRANT ALL PRIVILEGES ON gustos_db.* TO 'gustos_user'@'localhost';
FLUSH PRIVILEGES;
```

### 4.3 Estructura de Tablas (Migraciones)

```bash
# Desde el directorio backend
python manage.py migrate --database default

# Crear superusuario
python manage.py createsuperuser

# Cargar datos iniciales (opcional)
python manage.py seed_mvp
```

### 4.4 Respaldo Periódico

Script de backup diario (`/usr/local/bin/backup-gustos-db.sh`):

```bash
#!/bin/bash
BACKUP_DIR="/backups/gustos"
DATE=$(date +"%Y-%m-%d_%H-%M-%S")
BACKUP_FILE="$BACKUP_DIR/gustos_db_$DATE.sql.gz"

mkdir -p $BACKUP_DIR

mysqldump -u gustos_user -p$MYSQL_PASSWORD gustos_db | gzip > $BACKUP_FILE

# Mantener solo últimos 30 días
find $BACKUP_DIR -name "gustos_db_*.sql.gz" -mtime +30 -delete

echo "Backup completado: $BACKUP_FILE"
```

Configurar en crontab:

```bash
0 2 * * * /usr/local/bin/backup-gustos-db.sh >> /var/log/gustos-backup.log 2>&1
```

---

## 5. Despliegue del Backend (Django + Gunicorn)

### 5.1 Instalación de Python y Dependencias

```bash
# Crear entorno virtual
python3.11 -m venv /opt/gustos/venv

# Activar entorno
source /opt/gustos/venv/bin/activate

# Instalar dependencias
pip install --upgrade pip setuptools wheel
pip install -r backend/requirements/production.txt
```

### 5.2 Crear archivo `requirements/production.txt`

```
Django==4.2.11
djangorestframework==3.14.0
django-cors-headers==4.3.1
django-environ==0.11.2
mysqlclient==2.2.1
gunicorn==21.2.0
whitenoise==6.6.0
python-decouple==3.8
redis==5.0.1
celery==5.3.4
```

### 5.3 Configurar Gunicorn

Crear archivo `/etc/systemd/system/gustos-backend.service`:

```ini
[Unit]
Description=Gustos Backend - Django + Gunicorn
After=network.target mysql.service

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/opt/gustos
Environment="PATH=/opt/gustos/venv/bin"
Environment="DJANGO_SETTINGS_MODULE=config.settings"
EnvironmentFile=/opt/gustos/.env.production

ExecStart=/opt/gustos/venv/bin/gunicorn \
  --workers 4 \
  --worker-class sync \
  --bind unix:/run/gunicorn.sock \
  --timeout 60 \
  --access-logfile /var/log/gustos/gunicorn-access.log \
  --error-logfile /var/log/gustos/gunicorn-error.log \
  --log-level info \
  config.wsgi:application

Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
```

Habilitar y iniciar:

```bash
sudo systemctl daemon-reload
sudo systemctl enable gustos-backend
sudo systemctl start gustos-backend
```

### 5.4 Archivos Estáticos y Media

```bash
# Crear directorios
mkdir -p /var/www/gustos/{static,media}

# Recolectar archivos estáticos
python manage.py collectstatic --noinput --clear

# Permisos
sudo chown -R www-data:www-data /var/www/gustos
sudo chmod -R 755 /var/www/gustos
```

---

## 6. Despliegue del Frontend (Astro + Node.js)

### 6.1 Instalación de Node.js

```bash
# Usando nvm (recomendado)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 22.12.0
nvm use 22.12.0
```

O instalación de sistema:

```bash
# Ubuntu/Debian
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt-get install -y nodejs
```

### 6.2 Build de Astro

```bash
cd /opt/gustos/frontend
npm install

# Build optimizado
npm run build
```

### 6.3 Servir Frontend con Node.js

Crear `/etc/systemd/system/gustos-frontend.service`:

```ini
[Unit]
Description=Gustos Frontend - Astro Server
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/gustos/frontend
Environment="NODE_ENV=production"
Environment="PUBLIC_API_URL=https://api.example.com/api"

ExecStart=/opt/gustos/frontend/node_modules/.bin/astro preview \
  --host 127.0.0.1 \
  --port 3000

Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
```

Alternativamente, usar PM2:

```bash
npm install -g pm2

# Crear config PM2
cat > /opt/gustos/ecosystem.config.js << 'EOF'
module.exports = {
  apps: [
    {
      name: 'gustos-frontend',
      script: './node_modules/.bin/astro',
      args: 'preview --host 127.0.0.1 --port 3000',
      cwd: '/opt/gustos/frontend',
      instances: 'max',
      exec_mode: 'cluster',
      watch: false,
      env: {
        NODE_ENV: 'production',
        PUBLIC_API_URL: 'https://api.example.com/api'
      }
    }
  ]
};
EOF

pm2 start ecosystem.config.js
pm2 save
pm2 startup
```

---

## 7. Configuración de Nginx

### 7.1 Crear Virtual Host

Archivo `/etc/nginx/sites-available/gustos`:

```nginx
# Redirect HTTP to HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name example.com www.example.com;
    
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
    
    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS Main Server
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name example.com www.example.com;
    
    # SSL Certificates (Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    
    # Compression
    gzip on;
    gzip_types text/plain text/css text/xml text/javascript 
               application/json application/javascript application/xml+rss 
               application/atom+xml image/svg+xml;
    gzip_min_length 1000;
    
    # Frontend (Astro)
    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # API Backend (Django)
    location /api/ {
        proxy_pass http://unix:/run/gunicorn.sock;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }
    
    # Static Files
    location /static/ {
        alias /var/www/gustos/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # Media Files
    location /media/ {
        alias /var/www/gustos/media/;
        expires 7d;
        add_header Cache-Control "public";
    }
}
```

### 7.2 Habilitar y Probar

```bash
# Crear symlink
sudo ln -s /etc/nginx/sites-available/gustos /etc/nginx/sites-enabled/

# Remover default
sudo rm -f /etc/nginx/sites-enabled/default

# Probar configuración
sudo nginx -t

# Recargar Nginx
sudo systemctl reload nginx
```

---

## 8. SSL/TLS con Let's Encrypt

### 8.1 Instalación Inicial

```bash
sudo apt-get install certbot python3-certbot-nginx

# Generar certificado
sudo certbot certonly --nginx \
  -d example.com \
  -d www.example.com \
  --email admin@example.com \
  --agree-tos
```

### 8.2 Auto-Renovación

```bash
# Ver certificados
sudo certbot certificates

# Probar renovación
sudo certbot renew --dry-run

# Configurar renovación automática
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

---

## 9. Monitoreo y Logging

### 9.1 Archivos de Log

```bash
# Backend Gunicorn
tail -f /var/log/gustos/gunicorn-error.log
tail -f /var/log/gustos/gunicorn-access.log

# Nginx
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log

# Django (si está configurado)
tail -f /var/log/gustos/django.log
```

### 9.2 Monitoreo Básico con Supervisor

Crear `/etc/supervisor/conf.d/gustos.conf`:

```ini
[group:gustos]
programs=backend,frontend

[program:gustos-backend]
directory=/opt/gustos
command=/opt/gustos/venv/bin/gunicorn \
  --workers 4 \
  --bind unix:/run/gunicorn.sock \
  config.wsgi:application
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/gustos/backend.log

[program:gustos-frontend]
directory=/opt/gustos/frontend
command=npm run preview
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/gustos/frontend.log
environment=NODE_ENV=production,PUBLIC_API_URL=https://api.example.com/api
```

### 9.3 Monitoreo con Prometheus (opcional)

Instalar cliente Prometheus en Django:

```bash
pip install prometheus-client django-prometheus
```

---

## 10. Despliegue con Docker Compose (Producción)

### 10.1 Archivo `docker-compose.production.yml`

```yaml
version: '3.8'

services:
  mysql:
    image: mysql:8.4
    environment:
      MYSQL_ROOT_PASSWORD: ${DB_ROOT_PASSWORD}
      MYSQL_DATABASE: ${DB_NAME}
      MYSQL_USER: ${DB_USER}
      MYSQL_PASSWORD: ${DB_PASSWORD}
    volumes:
      - mysql_data:/var/lib/mysql
    ports:
      - "3306:3306"
    networks:
      - gustos_network
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      DEBUG: "False"
      DATABASE_URL: mysql://${DB_USER}:${DB_PASSWORD}@mysql:3306/${DB_NAME}
      SECRET_KEY: ${SECRET_KEY}
      ALLOWED_HOSTS: ${ALLOWED_HOSTS}
    depends_on:
      mysql:
        condition: service_healthy
    volumes:
      - static_volume:/opt/gustos/staticfiles
      - media_volume:/opt/gustos/media
    ports:
      - "8000:8000"
    networks:
      - gustos_network
    command: >
      sh -c "python manage.py migrate &&
             python manage.py collectstatic --noinput &&
             gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4"

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    environment:
      PUBLIC_API_URL: https://api.example.com/api
      NODE_ENV: production
    ports:
      - "3000:3000"
    networks:
      - gustos_network
    depends_on:
      - backend

  nginx:
    image: nginx:latest
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - static_volume:/var/www/gustos/static:ro
      - media_volume:/var/www/gustos/media:ro
      - /etc/letsencrypt:/etc/letsencrypt:ro
    depends_on:
      - backend
      - frontend
    networks:
      - gustos_network

volumes:
  mysql_data:
  static_volume:
  media_volume:

networks:
  gustos_network:
    driver: bridge
```

### 10.2 Dockerfile Backend

```dockerfile
FROM python:3.11-slim

WORKDIR /opt/gustos

# Install system dependencies
RUN apt-get update && apt-get install -y \
    mysql-client \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements/production.txt .
RUN pip install --no-cache-dir -r production.txt

# Copy application
COPY backend .

# Collect static files
RUN python manage.py collectstatic --noinput || true

EXPOSE 8000
```

### 10.3 Dockerfile Frontend

```dockerfile
FROM node:22-alpine

WORKDIR /opt/gustos/frontend

COPY frontend/package*.json ./
RUN npm ci

COPY frontend .

RUN npm run build

EXPOSE 3000

CMD ["npm", "run", "preview"]
```

### 10.4 Iniciar en Producción

```bash
docker-compose -f docker-compose.production.yml up -d
docker-compose -f docker-compose.production.yml logs -f
```

---

## 11. Escalabilidad y Performance

### 11.1 Optimización de Gunicorn

```bash
# Calcular workers óptimo
workers = (2 × CPU_cores) + 1

# Ejemplo: 4 cores = 9 workers
gunicorn --workers 9 \
         --worker-class sync \
         --worker-connections 1000 \
         --max-requests 1000 \
         --max-requests-jitter 50 \
         config.wsgi:application
```

### 11.2 Caché con Redis

Instalar Redis:

```bash
docker run -d \
  --name gustos-redis \
  -p 6379:6379 \
  redis:7-alpine
```

Configurar Django:

```python
# settings/production.py
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}
```

### 11.3 CDN y Distribución de Estáticos

Configurar S3/CloudFront (AWS):

```python
if not DEBUG:
    # Static files
    AWS_STORAGE_BUCKET_NAME = 'gustos-static'
    AWS_S3_REGION_NAME = 'us-east-1'
    STATIC_URL = f'https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/static/'
    STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
```

---

## 12. Monitoreo y Alertas

### 12.1 Health Checks

Endpoint en Django:

```python
# urls.py
from django.http import JsonResponse

def health_check(request):
    try:
        from django.db import connection
        connection.ensure_connection()
        return JsonResponse({"status": "ok", "database": "connected"})
    except Exception as e:
        return JsonResponse({"status": "error", "database": str(e)}, status=500)
```

Configurar Nginx para revisar:

```bash
curl -s https://example.com/health/ | jq .
```

### 12.2 Métricas con Prometheus

Instalar en Django:

```bash
pip install prometheus-client
```

Exposer métricas:

```python
# views.py
from prometheus_client import Counter, Histogram

request_count = Counter('app_requests_total', 'Total requests')
request_duration = Histogram('app_request_duration_seconds', 'Request duration')

@request_duration.time()
def my_view(request):
    request_count.inc()
    # ... view logic
```

---

## 13. Checklist Final de Despliegue

- [ ] Variables de entorno configuradas correctamente (`.env.production`)
- [ ] Base de datos MySQL instalada y migraciones aplicadas
- [ ] Secreto de Django generado y seguro
- [ ] Archivos estáticos recolectados
- [ ] Gunicorn configurado y en systemd
- [ ] Astro compilado y servido
- [ ] Nginx configurado con virtual hosts
- [ ] SSL/TLS con Let's Encrypt funcional
- [ ] Firewall configurado (UFW/iptables)
- [ ] Logs monitoreados
- [ ] Backups automáticos configurados
- [ ] Health checks funcionando
- [ ] Revisión de seguridad completada
- [ ] Tests de carga ejecutados

---

## 14. Troubleshooting

### 14.1 Problema: 502 Bad Gateway

```bash
# Verificar socket de Gunicorn
ls -la /run/gunicorn.sock

# Verificar logs
tail -f /var/log/gustos/gunicorn-error.log

# Reiniciar backend
sudo systemctl restart gustos-backend
```

### 14.2 Problema: Conexión a BD Rechazada

```bash
# Verificar MySQL está corriendo
sudo systemctl status mysql

# Probar conexión
mysql -u gustos_user -p -h localhost gustos_db

# Verificar credenciales en .env
grep DATABASE_URL .env.production
```

### 14.3 Problema: Archivos Estáticos No Se Cargan

```bash
# Recolectar estáticos
python manage.py collectstatic --noinput --clear

# Verificar permisos
ls -la /var/www/gustos/static/

# Recargar Nginx
sudo systemctl reload nginx
```

---

## Referencias y Documentación

- [Django Deployment Checklist](https://docs.djangoproject.com/en/4.2/deployment/checklist/)
- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [Astro Deployment Guide](https://docs.astro.build/en/guides/deploy/)
- [Nginx Best Practices](https://nginx.org/en/docs/)
- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)
- [Docker & Docker Compose](https://docs.docker.com/)
- [MySQL 8.4 Reference Manual](https://dev.mysql.com/doc/)

---

**Documento generado:** 2026-06-20
**Versión:** 1.0
**Autor:** Equipo de Desarrollo Gustos y Sabores
