from django.db import IntegrityError, transaction
from django.test import TestCase
from rest_framework.test import APIClient

from apps.menu.models import Category, Dish
from apps.orders.models import Order, OrderItem


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

    def test_rejects_unavailable_dish(self):
        category = Category.objects.create(name="Fondos")
        dish = Dish.objects.create(category=category, name="Agotado", price="28.00", is_available=False)
        payload = {
            "customer_name": "Cliente Demo",
            "customer_email": "cliente@example.com",
            "customer_phone": "999999999",
            "order_type": "local",
            "payment_method": "cash",
            "items": [{"dish_id": dish.id, "quantity": 1}],
        }

        response = APIClient().post("/api/orders/", payload, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Order.objects.count(), 0)

    def test_order_item_quantity_must_be_positive(self):
        category = Category.objects.create(name="Fondos")
        dish = Dish.objects.create(category=category, name="Lomo saltado", price="28.00")
        order = Order.objects.create(customer_name="Demo", customer_email="demo@example.com", customer_phone="999999999")

        with self.assertRaises(IntegrityError), transaction.atomic():
            OrderItem.objects.create(order=order, dish=dish, quantity=0, unit_price=dish.price)
