from django.test import TestCase
from rest_framework.test import APIClient

from apps.menu.models import Category, Dish


class OrderApiTests(TestCase):
    def test_creates_order_with_item_and_total(self):
        category = Category.objects.create(name="Fondos")
        dish = Dish.objects.create(category=category, name="Lomo saltado", price="28.00")
        payload = {
            "customer_name": "Cliente Demo",
            "customer_email": "cliente@example.com",
            "customer_phone": "999999999",
            "order_type": "local",
            "payment_method": "cash",
            "items": [{"dish_id": dish.id, "quantity": 2}],
        }

        response = APIClient().post("/api/orders/", payload, format="json")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["total"], "56.00")
