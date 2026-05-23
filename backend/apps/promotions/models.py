from django.db import models
from django.db.models import Q
from django.utils import timezone

from apps.common.models import TimeStampedModel


class Promotion(TimeStampedModel):
    class DiscountType(models.TextChoices):
        PERCENTAGE = "percentage", "Porcentaje"
        FIXED = "fixed", "Monto fijo"

    name = models.CharField(max_length=200, verbose_name="Nombre")
    description = models.TextField(blank=True, verbose_name="Descripción")
    code = models.CharField(max_length=50, unique=True, blank=True, verbose_name="Código")
    discount_type = models.CharField(
        max_length=20,
        choices=DiscountType.choices,
        default=DiscountType.PERCENTAGE,
        verbose_name="Tipo de descuento",
    )
    discount_value = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Valor del descuento"
    )
    min_order_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="Monto mínimo de pedido"
    )
    starts_at = models.DateTimeField(verbose_name="Fecha de inicio")
    ends_at = models.DateTimeField(verbose_name="Fecha de fin")
    is_active = models.BooleanField(default=True, verbose_name="Activa")
    usage_limit = models.PositiveIntegerField(
        null=True, blank=True, verbose_name="Límite de usos"
    )
    times_used = models.PositiveIntegerField(default=0, verbose_name="Veces utilizada")

    class Meta:
        verbose_name = "Promoción"
        verbose_name_plural = "Promociones"
        ordering = ("-starts_at",)
        constraints = [
            models.CheckConstraint(
                check=Q(discount_value__gt=0), name="promotion_discount_gt_0"
            )
        ]

    def is_valid(self):
        now = timezone.now()
        within_dates = self.starts_at <= now <= self.ends_at
        within_limit = self.usage_limit is None or self.times_used < self.usage_limit
        return self.is_active and within_dates and within_limit

    def __str__(self) -> str:
        return f"{self.name} ({self.code})"
