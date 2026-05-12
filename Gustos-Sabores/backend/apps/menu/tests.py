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
