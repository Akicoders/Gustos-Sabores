import os
import django
from datetime import datetime, timedelta

# Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.utils import timezone
from apps.users.models import User
from apps.menu.models import Category, Dish
from apps.inventory.models import InventoryItem, StockMovement
from apps.suppliers.models import Supplier, SupplierProduct
from apps.promotions.models import Promotion
from apps.orders.models import Order, OrderItem
from apps.reservations.models import Reservation

def run_seed():
    print("Iniciando carga de datos de ejemplo (seed)...")

    # 1. Usuarios
    print("- Creando usuarios...")
    admin, created = User.objects.get_or_create(username='admin', defaults={
        'email': 'admin@gustos.com', 'role': 'admin', 'is_staff': True, 'is_superuser': True
    })
    if created: admin.set_password('admin123'); admin.save()

    staff, created = User.objects.get_or_create(username='staff', defaults={
        'email': 'staff@gustos.com', 'role': 'staff', 'is_staff': True
    })
    if created: staff.set_password('staff123'); staff.save()

    customer, created = User.objects.get_or_create(username='cliente1', defaults={
        'email': 'cliente1@gustos.com', 'role': 'customer', 'phone': '987654321', 'full_name': 'Juan Pérez'
    })
    if created: customer.set_password('cliente123'); customer.save()

    # 2. Categorías de Menú
    print("- Creando menú...")
    cat_entradas, _ = Category.objects.get_or_create(name='Entradas', description='Entradas y piqueos')
    cat_fondos, _ = Category.objects.get_or_create(name='Platos de Fondo', description='Nuestros mejores platos')
    cat_bebidas, _ = Category.objects.get_or_create(name='Bebidas', description='Gaseosas, refrescos y más')

    # 3. Platos
    d1, _ = Dish.objects.get_or_create(name='Ceviche Clásico', defaults={'category': cat_entradas, 'price': 25.00, 'cost_price': 10.00, 'description': 'Ceviche de pescado fresco con limón y ají.'})
    d2, _ = Dish.objects.get_or_create(name='Lomo Saltado', defaults={'category': cat_fondos, 'price': 35.00, 'cost_price': 15.00, 'description': 'Trozos de lomo de res saltados con cebolla y tomate.'})
    d3, _ = Dish.objects.get_or_create(name='Chicha Morada (Jarra)', defaults={'category': cat_bebidas, 'price': 15.00, 'cost_price': 5.00, 'description': 'Refrescante chicha morada natural.'})

    # 4. Inventario y Proveedores
    print("- Creando inventario y proveedores...")
    prov1, _ = Supplier.objects.get_or_create(name='Mercado Sur', defaults={'ruc': '20123456789', 'contact_name': 'Carlos'})
    prov2, _ = Supplier.objects.get_or_create(name='Bebidas SAC', defaults={'ruc': '20987654321', 'contact_name': 'Ana'})

    inv1, _ = InventoryItem.objects.get_or_create(name='Pescado Fresco', defaults={'unit': 'kg', 'stock': 20.0, 'min_stock': 5.0, 'cost_price': 20.00})
    inv2, _ = InventoryItem.objects.get_or_create(name='Lomo de Res', defaults={'unit': 'kg', 'stock': 10.0, 'min_stock': 3.0, 'cost_price': 30.00})
    inv3, _ = InventoryItem.objects.get_or_create(name='Botellas Gaseosa', defaults={'unit': 'unidad', 'stock': 50.0, 'min_stock': 20.0, 'cost_price': 2.50})

    SupplierProduct.objects.get_or_create(supplier=prov1, item=inv1, defaults={'price': 19.50})
    SupplierProduct.objects.get_or_create(supplier=prov2, item=inv3, defaults={'price': 2.50})

    # 5. Promociones
    print("- Creando promociones...")
    promo1, _ = Promotion.objects.get_or_create(code='BIENVENIDO20', defaults={
        'name': 'Descuento Nuevo Cliente', 'discount_type': 'percentage', 'discount_value': 20.00,
        'min_order_amount': 50.00, 'starts_at': timezone.now(), 'ends_at': timezone.now() + timedelta(days=30)
    })
    
    # 6. Pedidos (con datos pasados para gráficos)
    print("- Creando pedidos de ejemplo...")
    if Order.objects.count() == 0:
        o1 = Order.objects.create(customer=customer, total=60.00, subtotal=75.00, status='completed', order_type='delivery', address='Av. Pardo 123', payment_method='card', promotion=promo1, discount_amount=15.00)
        o1.created_at = timezone.now() - timedelta(days=2); o1.save()
        OrderItem.objects.create(order=o1, dish=d1, quantity=1, unit_price=25.00)
        OrderItem.objects.create(order=o1, dish=d2, quantity=1, unit_price=35.00)
        OrderItem.objects.create(order=o1, dish=d3, quantity=1, unit_price=15.00)

        o2 = Order.objects.create(customer=customer, total=25.00, subtotal=25.00, status='pending', order_type='pickup', payment_method='cash')
        OrderItem.objects.create(order=o2, dish=d1, quantity=1, unit_price=25.00)

    # 7. Reservas
    print("- Creando reservas...")
    if Reservation.objects.count() == 0:
        Reservation.objects.create(
            customer=customer, customer_name='Juan Pérez', customer_phone='987654321', customer_email='cliente1@gustos.com',
            party_size=4, reserved_at=timezone.now() + timedelta(days=1, hours=2), status='confirmed', notes='Mesa cerca a la ventana'
        )

    print("¡Datos de ejemplo creados exitosamente!")

if __name__ == '__main__':
    run_seed()
