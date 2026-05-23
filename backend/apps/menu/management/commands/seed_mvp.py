from decimal import Decimal
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.menu.models import Category, Dish
from apps.orders.models import Order, OrderItem
from apps.reservations.models import Reservation


SEED_DATA = {
    "Entradas": [
        ("Causa limena", "Causa de pollo con palta y salsa criolla.", "18.50", "https://images.unsplash.com/photo-1625938145744-e3805153993d?auto=format&fit=crop&w=900&q=80"),
        ("Papa a la huancaina", "Papas en salsa cremosa de aji amarillo.", "16.00", "https://images.unsplash.com/photo-1601314002592-b8734bca6604?auto=format&fit=crop&w=900&q=80"),
        ("Ceviche clasico", "Pescado fresco, limon, camote, choclo y cebolla roja.", "42.00", "https://images.unsplash.com/photo-1626200419199-391ae4be7a41?auto=format&fit=crop&w=900&q=80"),
        ("Choclo con queso", "Choclo tierno acompanado con queso fresco artesanal.", "14.50", "https://images.unsplash.com/photo-1551754655-cd27e38d2076?auto=format&fit=crop&w=900&q=80"),
        ("Tequenos criollos", "Tequenos dorados con salsa de aji amarillo.", "17.00", "https://images.unsplash.com/photo-1562967916-eb82221dfb36?auto=format&fit=crop&w=900&q=80"),
    ],
    "Fondos": [
        ("Arroz con pato", "Arroz norteno con culantro y pato tierno.", "34.90", "https://images.unsplash.com/photo-1603133872878-684f208fb84b?auto=format&fit=crop&w=900&q=80"),
        ("Seco de cabrito", "Cabrito al estilo lambayecano con frejoles.", "36.50", "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=900&q=80"),
        ("Lomo saltado", "Salteado clasico de res con papas y arroz.", "28.00", "https://images.unsplash.com/photo-1529692236671-f1f6cf9683ba?auto=format&fit=crop&w=900&q=80"),
        ("Ají de gallina", "Crema suave de aji amarillo con pollo deshilachado y arroz.", "26.00", "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?auto=format&fit=crop&w=900&q=80"),
        ("Tacu tacu con lomo", "Tacu tacu crocante servido con lomo jugoso.", "33.00", "https://images.unsplash.com/photo-1555939594-58d7cb561ad1?auto=format&fit=crop&w=900&q=80"),
        ("Cabrito norteño", "Cabrito guisado con loche, yuca y frejoles.", "39.00", "https://images.unsplash.com/photo-1604908176997-125f25cc6f3d?auto=format&fit=crop&w=900&q=80"),
        ("Arroz chaufa criollo", "Chaufa salteado al wok con insumos locales.", "24.50", "https://images.unsplash.com/photo-1512058564366-18510be2db19?auto=format&fit=crop&w=900&q=80"),
    ],
    "Bebidas": [
        ("Chicha morada", "Bebida tradicional de maiz morado.", "8.50", "https://images.unsplash.com/photo-1544145945-f90425340c7e?auto=format&fit=crop&w=900&q=80"),
        ("Maracuya frozen", "Refresco frio de maracuya.", "9.00", "https://images.unsplash.com/photo-1497534446932-c925b458314e?auto=format&fit=crop&w=900&q=80"),
        ("Limonada hierbabuena", "Limonada fresca con hierbabuena y hielo.", "8.00", "https://images.unsplash.com/photo-1621263764928-df1444c5e859?auto=format&fit=crop&w=900&q=80"),
        ("Emoliente frio", "Infusion andina servida fria con linaza y cebada.", "7.50", "https://images.unsplash.com/photo-1556679343-c7306c1976bc?auto=format&fit=crop&w=900&q=80"),
        ("Inca Kola personal", "Gaseosa personal para acompanar el menu.", "6.00", "https://images.unsplash.com/photo-1581006852262-e4307cf6283a?auto=format&fit=crop&w=900&q=80"),
        ("Agua mineral", "Agua sin gas en botella personal.", "5.00", "https://images.unsplash.com/photo-1523362628745-0c100150b504?auto=format&fit=crop&w=900&q=80"),
    ],
}


from apps.users.models import User

class Command(BaseCommand):
    help = "Carga categorias y platos iniciales para el MVP."

    def handle(self, *args, **options):
        # Crear usuarios demo
        self.stdout.write("Creando usuarios demo...")
        admin, created = User.objects.get_or_create(username='admin', defaults={
            'email': 'admin@gustos.com', 'role': 'admin', 'is_staff': True, 'is_superuser': True
        })
        if created:
            admin.set_password('admin123')
            admin.save()
            self.stdout.write("Usuario 'admin' / 'admin123' creado.")

        staff, created = User.objects.get_or_create(username='staff', defaults={
            'email': 'staff@gustos.com', 'role': 'staff', 'is_staff': True
        })
        if created:
            staff.set_password('staff123')
            staff.save()
            self.stdout.write("Usuario 'staff' / 'staff123' creado.")

        created = 0
        for category_name, dishes in SEED_DATA.items():
            category, _ = Category.objects.get_or_create(name=category_name)
            for name, description, price, image_url in dishes:
                dish, was_created = Dish.objects.get_or_create(
                    category=category,
                    name=name,
                    defaults={"description": description, "price": price, "image_url": image_url, "is_available": True},
                )
                if not was_created:
                    dish.description = description
                    dish.price = price
                    dish.image_url = image_url
                    dish.is_available = True
                    dish.save(update_fields=["description", "price", "image_url", "is_available"])
                created += int(was_created)
        self.seed_demo_activity()
        self.stdout.write(self.style.SUCCESS(f"Seed MVP completado. Nuevos platos: {created}"))

    def seed_demo_activity(self):
        from apps.billing.models import Invoice
        demo_orders = Order.objects.filter(notes="demo-seed")
        Invoice.objects.filter(order__in=demo_orders).delete()
        demo_orders.delete()
        Reservation.objects.filter(notes="demo-seed").delete()

        demo_orders = [
            ("Ana Torres", "ana@example.com", "999111222", "delivered", [("Arroz con pato", 2), ("Chicha morada", 2)]),
            ("Luis Rojas", "luis@example.com", "999333444", "delivered", [("Lomo saltado", 1), ("Maracuya frozen", 1)]),
            ("Dante Valerius", "dante@example.com", "999555666", "preparing", [("Cabrito norteño", 1), ("Limonada hierbabuena", 1)]),
            ("Maria Castillo", "maria@example.com", "999777888", "pending", [("Ceviche clasico", 1), ("Agua mineral", 1)]),
            ("Paolo Vega", "paolo@example.com", "999999000", "ready", [("Tacu tacu con lomo", 1), ("Inca Kola personal", 2)]),
            ("Rosa Medina", "rosa@example.com", "988111222", "delivered", [("Ají de gallina", 2), ("Emoliente frio", 2)]),
        ]

        for customer_name, email, phone, status, items in demo_orders:
            order = Order.objects.create(
                customer_name=customer_name,
                customer_email=email,
                customer_phone=phone,
                order_type=Order.OrderType.LOCAL,
                payment_method=Order.PaymentMethod.CASH,
                status=status,
                notes="demo-seed",
            )
            total = Decimal("0.00")
            for dish_name, quantity in items:
                dish = Dish.objects.get(name=dish_name)
                OrderItem.objects.create(order=order, dish=dish, quantity=quantity, unit_price=dish.price)
                total += dish.price * quantity
            order.total = total
            order.save(update_fields=["total"])

        now = timezone.now()
        demo_reservations = [
            ("Carlos Peña", "carlos@example.com", "977111222", 2, Reservation.Status.CONFIRMED, 1),
            ("Lucia Ramos", "lucia@example.com", "977333444", 5, Reservation.Status.PENDING, 2),
            ("Equipo UTP", "utp@example.com", "977555666", 8, Reservation.Status.CONFIRMED, 3),
            ("Familia Cruz", "cruz@example.com", "977777888", 4, Reservation.Status.CANCELLED, 4),
            ("Andrea Silva", "andrea@example.com", "977999000", 3, Reservation.Status.CONFIRMED, 5),
            ("Martín Vizcarra", "martin@example.com", "955123456", 6, Reservation.Status.PENDING, 1),
            ("Gabriela Mistral", "gabi@example.com", "955987654", 4, Reservation.Status.CONFIRMED, 2),
            ("César Vallejo", "cesar@example.com", "944555111", 2, Reservation.Status.PENDING, 3),
            ("Gastón Acurio", "gaston@example.com", "988777222", 10, Reservation.Status.CONFIRMED, 1),
            ("Rosa Maria", "rosa@example.com", "911222333", 4, Reservation.Status.CANCELLED, 2),
            ("José Sabogal", "jose@example.com", "922444666", 5, Reservation.Status.CONFIRMED, 4),
        ]

        for name, email, phone, party_size, status, days in demo_reservations:
            Reservation.objects.create(
                customer_name=name,
                customer_email=email,
                customer_phone=phone,
                reserved_at=now + timedelta(days=days),
                party_size=party_size,
                status=status,
                notes="demo-seed",
            )
