from django.db import IntegrityError, transaction
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from apps.reservations.models import Reservation


class ReservationApiTests(TestCase):
    def test_creates_pending_reservation(self):
        payload = {
            "customer_name": "Cliente Reserva",
            "customer_email": "reserva@example.com",
            "customer_phone": "988888888",
            "reserved_at": (timezone.now() + timezone.timedelta(days=1)).isoformat(),
            "party_size": 4,
        }

        response = APIClient().post("/api/reservations/", payload, format="json")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["status"], "pending")

    def test_rejects_past_reservation(self):
        payload = {
            "customer_name": "Cliente Reserva",
            "customer_email": "reserva@example.com",
            "customer_phone": "988888888",
            "reserved_at": (timezone.now() - timezone.timedelta(hours=1)).isoformat(),
            "party_size": 4,
        }

        response = APIClient().post("/api/reservations/", payload, format="json")

        self.assertEqual(response.status_code, 400)

    def test_rejects_zero_party_size(self):
        payload = {
            "customer_name": "Cliente Reserva",
            "customer_email": "reserva@example.com",
            "customer_phone": "988888888",
            "reserved_at": (timezone.now() + timezone.timedelta(days=1)).isoformat(),
            "party_size": 0,
        }

        response = APIClient().post("/api/reservations/", payload, format="json")

        self.assertEqual(response.status_code, 400)

    def test_party_size_must_be_positive(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Reservation.objects.create(
                customer_name="Cliente Reserva",
                customer_email="reserva@example.com",
                customer_phone="988888888",
                reserved_at=timezone.now() + timezone.timedelta(days=1),
                party_size=0,
            )
