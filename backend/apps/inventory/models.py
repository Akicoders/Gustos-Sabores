from django.conf import settings
from django.db import models
from django.db.models import Q

from apps.common.models import TimeStampedModel


class InventoryItem(TimeStampedModel):
    class Unit(models.TextChoices):
        UNIT = "unidad", "Unidad"
        KG = "kg", "Kilogramo"
        GRAM = "g", "Gramo"
        LITER = "l", "Litro"
        ML = "ml", "Mililitro"

    name = models.CharField(max_length=200, unique=True, verbose_name="Nombre")
    unit = models.CharField(
        max_length=20, choices=Unit.choices, default=Unit.UNIT, verbose_name="Unidad"
    )
    stock = models.DecimalField(
        max_digits=12, decimal_places=3, default=0, verbose_name="Stock actual"
    )
    min_stock = models.DecimalField(
        max_digits=12, decimal_places=3, default=0, verbose_name="Stock mínimo (alerta)"
    )
    cost_price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="Precio de costo"
    )
    notes = models.TextField(blank=True, verbose_name="Notas")

    class Meta:
        verbose_name = "Artículo de inventario"
        verbose_name_plural = "Artículos de inventario"
        ordering = ("name",)
        constraints = [
            models.CheckConstraint(check=Q(stock__gte=0), name="inventory_stock_gte_0"),
            models.CheckConstraint(check=Q(min_stock__gte=0), name="inventory_min_stock_gte_0"),
        ]

    @property
    def is_low_stock(self) -> bool:
        return self.stock <= self.min_stock

    def __str__(self) -> str:
        return f"{self.name} ({self.stock} {self.unit})"


class StockMovement(models.Model):
    class MovementType(models.TextChoices):
        IN = "in", "Entrada"
        OUT = "out", "Salida"
        ADJUSTMENT = "adjustment", "Ajuste"

    item = models.ForeignKey(
        InventoryItem,
        related_name="movements",
        on_delete=models.CASCADE,
        verbose_name="Artículo",
    )
    movement_type = models.CharField(
        max_length=20,
        choices=MovementType.choices,
        verbose_name="Tipo de movimiento",
    )
    quantity = models.DecimalField(
        max_digits=12, decimal_places=3, verbose_name="Cantidad"
    )
    notes = models.TextField(blank=True, verbose_name="Referencia / motivo")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="Registrado por",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Movimiento de stock"
        verbose_name_plural = "Movimientos de stock"
        ordering = ("-created_at",)

    def save(self, *args, **kwargs):
        if self.movement_type == self.MovementType.IN:
            self.item.stock += self.quantity
        elif self.movement_type == self.MovementType.OUT:
            self.item.stock -= self.quantity
        else:
            # Ajuste: quantity es el nuevo valor absoluto
            self.item.stock = self.quantity
        self.item.save(update_fields=["stock"])
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.get_movement_type_display()} {self.quantity} {self.item.unit} de {self.item.name}"
