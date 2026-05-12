from django.core.management.base import BaseCommand

from apps.menu.models import Category, Dish


SEED_DATA = {
    "Entradas": [
        ("Causa limena", "Causa de pollo con palta y salsa criolla.", "18.50"),
        ("Papa a la huancaina", "Papas en salsa cremosa de aji amarillo.", "16.00"),
    ],
    "Fondos": [
        ("Arroz con pato", "Arroz norteno con culantro y pato tierno.", "34.90"),
        ("Seco de cabrito", "Cabrito al estilo lambayecano con frejoles.", "36.50"),
        ("Lomo saltado", "Salteado clasico de res con papas y arroz.", "28.00"),
    ],
    "Bebidas": [
        ("Chicha morada", "Bebida tradicional de maiz morado.", "8.50"),
        ("Maracuya frozen", "Refresco frio de maracuya.", "9.00"),
    ],
}


class Command(BaseCommand):
    help = "Carga categorias y platos iniciales para el MVP."

    def handle(self, *args, **options):
        created = 0
        for category_name, dishes in SEED_DATA.items():
            category, _ = Category.objects.get_or_create(name=category_name)
            for name, description, price in dishes:
                _, was_created = Dish.objects.get_or_create(
                    category=category,
                    name=name,
                    defaults={"description": description, "price": price, "is_available": True},
                )
                created += int(was_created)
        self.stdout.write(self.style.SUCCESS(f"Seed MVP completado. Nuevos platos: {created}"))
