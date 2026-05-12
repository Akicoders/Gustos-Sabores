from django.conf import settings
from django.db import models

from apps.common.models import TimeStampedModel


class Reservation(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pendiente"
        CONFIRMED = "confirmed", "Confirmada"
        CANCELLED = "cancelled", "Cancelada"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="reservations", on_delete=models.SET_NULL, null=True, blank=True)
    customer_name = models.CharField(max_length=255)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=30)
    reserved_at = models.DateTimeField()
    party_size = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ("-reserved_at",)

    def __str__(self) -> str:
        return f"Reserva #{self.pk} - {self.customer_name}"
