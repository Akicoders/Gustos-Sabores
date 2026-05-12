from django.db import IntegrityError, transaction
from django.test import TestCase
from rest_framework.test import APIClient

from apps.menu.models import Category, Dish


class MenuApiTests(TestCase):
    def test_lists_available_dishes(self):
        category = Category.objects.create(name="Fondos")
        Dish.objects.create(category=category, name="Arroz con pato", price="34.90")

        response = APIClient().get("/api/menu/dishes/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]["name"], "Arroz con pato")

    def test_hides_unavailable_dishes_and_empty_categories(self):
        available_category = Category.objects.create(name="Fondos")
        hidden_category = Category.objects.create(name="Ocultos")
        Dish.objects.create(category=available_category, name="Lomo saltado", price="28.00", is_available=True)
        Dish.objects.create(category=hidden_category, name="Plato agotado", price="20.00", is_available=False)

        client = APIClient()
        dishes_response = client.get("/api/menu/dishes/")
        categories_response = client.get("/api/menu/categories/")

        self.assertEqual([dish["name"] for dish in dishes_response.data], ["Lomo saltado"])
        self.assertEqual([category["name"] for category in categories_response.data], ["Fondos"])
        self.assertEqual(categories_response.data[0]["dishes"][0]["name"], "Lomo saltado")

    def test_dish_price_cannot_be_negative(self):
        category = Category.objects.create(name="Fondos")

        with self.assertRaises(IntegrityError), transaction.atomic():
            Dish.objects.create(category=category, name="Precio invalido", price="-1.00")
