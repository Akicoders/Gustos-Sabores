from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient


class ReservationApiTests(TestCase):
    def test_creates_pending_reservation(self):
        payload = {
            "customer_name": "Cliente Reserva",
            "customer_email": "reserva@example.com",
            "customer_phone": "988888888",
            "reserved_at": timezone.now().isoformat(),
            "party_size": 4,
        }

        response = APIClient().post("/api/reservations/", payload, format="json")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["status"], "pending")
