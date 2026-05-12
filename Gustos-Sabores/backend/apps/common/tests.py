from django.test import TestCase
from rest_framework.test import APIClient

from apps.menu.models import Category, Dish
from apps.users.models import User


class DashboardKPITests(TestCase):
    def test_dashboard_kpis_include_menu_counts(self):
        category = Category.objects.create(name="Bebidas")
        Dish.objects.create(category=category, name="Chicha morada", price="8.50")
        user = User.objects.create_user(
            username="staff",
            email="staff@example.com",
            full_name="Staff Demo",
            password="strong-pass-123",
            role=User.Roles.STAFF,
        )
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get("/api/dashboard/kpis/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["dishes_total"], 1)
        self.assertEqual(response.data["menu_by_category"]["Bebidas"], 1)

    def test_dashboard_kpis_require_staff_or_admin(self):
        client = APIClient()
        customer = User.objects.create_user(
            username="customer",
            email="customer@example.com",
            full_name="Customer Demo",
            password="strong-pass-123",
        )

        anonymous_response = client.get("/api/dashboard/kpis/")
        client.force_authenticate(user=customer)
        customer_response = client.get("/api/dashboard/kpis/")

        self.assertEqual(anonymous_response.status_code, 401)
        self.assertEqual(customer_response.status_code, 403)
