from django.test import TestCase
from rest_framework.test import APIClient

from apps.menu.models import Category, Dish


class DashboardKPITests(TestCase):
    def test_dashboard_kpis_include_menu_counts(self):
        category = Category.objects.create(name="Bebidas")
        Dish.objects.create(category=category, name="Chicha morada", price="8.50")

        response = APIClient().get("/api/dashboard/kpis/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["dishes_total"], 1)
        self.assertEqual(response.data["menu_by_category"]["Bebidas"], 1)
