# MVP 1

## Objetivo

Entregar una base realizable del sistema con flujo publico de menu, pedidos y reservas, mas una capa administrativa inicial para operacion interna.

## Alcance incluido

- landing publica
- pagina de menu conectada a API
- formulario de reservas
- formulario de pedidos
- autenticacion por token para clientes
- backend con modelos base y panel admin
- entorno local reproducible con Docker Compose

## Alcance no incluido aun

- pasarela de pagos
- redis en runtime
- inventario operativo
- reportes avanzados
- notificaciones por correo o WhatsApp
- flujo de repartidores

## Criterio de realizable

El proyecto puede levantarse en local, persistir datos, exponer API y permitir registrar reservas y pedidos desde la web.
