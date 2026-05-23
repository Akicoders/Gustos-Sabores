from datetime import timedelta
from decimal import Decimal

from django.db import IntegrityError, transaction
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from apps.menu.models import Category, Dish
from apps.orders.models import Order, OrderItem
from apps.promotions.models import Promotion


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


class OrderBusinessRulesTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Fondos")
        self.dish = Dish.objects.create(category=self.category, name="Lomo saltado", price="100.00")

    def _payload(self, **overrides):
        payload = {
            "customer_name": "Cliente Demo",
            "customer_email": "cliente@example.com",
            "customer_phone": "999999999",
            "order_type": "local",
            "payment_method": "cash",
            "items": [{"dish_id": self.dish.id, "quantity": 1}],
        }
        payload.update(overrides)
        return payload

    def test_delivery_requires_address(self):
        response = APIClient().post("/api/orders/", self._payload(order_type="delivery"), format="json")

        self.assertEqual(response.status_code, 400)
        self.assertIn("delivery_address", response.data)
        self.assertEqual(Order.objects.count(), 0)

    def test_delivery_with_address_succeeds(self):
        payload = self._payload(order_type="delivery", delivery_address="Av. Siempre Viva 742")

        response = APIClient().post("/api/orders/", payload, format="json")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Order.objects.get().delivery_address, "Av. Siempre Viva 742")

    def test_captures_historical_unit_price(self):
        response = APIClient().post("/api/orders/", self._payload(items=[{"dish_id": self.dish.id, "quantity": 2}]), format="json")

        self.assertEqual(response.status_code, 201)
        item = Order.objects.get().items.first()
        self.assertEqual(item.unit_price, Decimal("100.00"))

    def test_applies_percentage_promotion(self):
        Promotion.objects.create(
            name="Bienvenida",
            code="BIENVENIDA10",
            discount_type=Promotion.DiscountType.PERCENTAGE,
            discount_value="10.00",
            min_order_amount="0.00",
            starts_at=timezone.now() - timedelta(days=1),
            ends_at=timezone.now() + timedelta(days=1),
        )

        response = APIClient().post("/api/orders/", self._payload(promotion_code="BIENVENIDA10"), format="json")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["subtotal"], "100.00")
        self.assertEqual(response.data["discount_amount"], "10.00")
        self.assertEqual(response.data["total"], "90.00")

    def test_applies_fixed_promotion(self):
        Promotion.objects.create(
            name="Cupón fijo",
            code="MENOS20",
            discount_type=Promotion.DiscountType.FIXED,
            discount_value="20.00",
            min_order_amount="50.00",
            starts_at=timezone.now() - timedelta(days=1),
            ends_at=timezone.now() + timedelta(days=1),
        )

        response = APIClient().post("/api/orders/", self._payload(promotion_code="menos20"), format="json")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["discount_amount"], "20.00")
        self.assertEqual(response.data["total"], "80.00")

    def test_ignores_unknown_promotion_code(self):
        response = APIClient().post("/api/orders/", self._payload(promotion_code="NOEXISTE"), format="json")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["discount_amount"], "0.00")
        self.assertEqual(response.data["total"], "100.00")

    def test_promotion_below_min_amount_not_applied(self):
        Promotion.objects.create(
            name="Gran pedido",
            code="GRANDE",
            discount_type=Promotion.DiscountType.FIXED,
            discount_value="20.00",
            min_order_amount="500.00",
            starts_at=timezone.now() - timedelta(days=1),
            ends_at=timezone.now() + timedelta(days=1),
        )

        response = APIClient().post("/api/orders/", self._payload(promotion_code="GRANDE"), format="json")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["discount_amount"], "0.00")
