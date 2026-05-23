from decimal import Decimal

from django.conf import settings
from django.db import models
from django.db.models import Q

from apps.common.models import TimeStampedModel
from apps.menu.models import Dish


class Order(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pendiente"
        PREPARING = "preparing", "En preparacion"
        READY = "ready", "Listo"
        DELIVERED = "delivered", "Entregado"
        CANCELLED = "cancelled", "Cancelado"

    class OrderType(models.TextChoices):
        LOCAL = "local", "Local"
        DELIVERY = "delivery", "Delivery"

    class PaymentMethod(models.TextChoices):
        CASH = "cash", "Contra entrega"
        YAPE = "yape", "Yape"
        CARD = "card", "Tarjeta"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="orders", on_delete=models.SET_NULL, null=True, blank=True)
    customer_name = models.CharField(max_length=255)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=30)
    delivery_address = models.CharField(max_length=255, blank=True)
    order_type = models.CharField(max_length=20, choices=OrderType.choices, default=OrderType.LOCAL)
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices, default=PaymentMethod.CASH)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    notes = models.TextField(blank=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    promotion = models.ForeignKey(
        "promotions.Promotion",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="orders",
        verbose_name="Promoción aplicada",
    )

    class Meta:
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"Pedido #{self.pk} - {self.customer_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    dish = models.ForeignKey(Dish, related_name="order_items", on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        constraints = [models.CheckConstraint(check=Q(quantity__gt=0), name="orderitem_quantity_gt_0")]

    def __str__(self) -> str:
        return f"{self.quantity} x {self.dish.name}"
