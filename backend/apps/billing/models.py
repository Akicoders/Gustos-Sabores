from decimal import Decimal

from django.conf import settings
from django.db import models

from apps.common.models import TimeStampedModel
from apps.orders.models import Order


class Invoice(TimeStampedModel):
    class InvoiceType(models.TextChoices):
        BOLETA = "boleta", "Boleta de venta"
        FACTURA = "factura", "Factura"

    # Datos del comprobante
    invoice_type = models.CharField(
        max_length=20,
        choices=InvoiceType.choices,
        default=InvoiceType.BOLETA,
        verbose_name="Tipo de comprobante",
    )
    series = models.CharField(max_length=4, default="B001", verbose_name="Serie")
    correlative = models.PositiveIntegerField(verbose_name="Correlativo")

    # Pedido asociado
    order = models.OneToOneField(
        Order,
        related_name="invoice",
        on_delete=models.PROTECT,
        verbose_name="Pedido",
    )

    # Datos del receptor (cliente)
    receptor_name = models.CharField(max_length=255, verbose_name="Nombre / Razón social")
    receptor_doc = models.CharField(max_length=20, blank=True, verbose_name="DNI / RUC")
    receptor_address = models.CharField(max_length=255, blank=True, verbose_name="Dirección")
    receptor_email = models.EmailField(blank=True, verbose_name="Correo del receptor")

    # Montos
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Subtotal")
    igv = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="IGV (18%)")
    total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Total")
    discount = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00"), verbose_name="Descuento"
    )

    # Quién emitió
    issued_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="Emitido por",
    )

    class Meta:
        verbose_name = "Comprobante"
        verbose_name_plural = "Comprobantes"
        ordering = ("-created_at",)
        unique_together = ("series", "correlative")

    @property
    def number(self) -> str:
        return f"{self.series}-{str(self.correlative).zfill(8)}"

    def __str__(self) -> str:
        return f"{self.get_invoice_type_display()} {self.number}"


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(
        Invoice, related_name="items", on_delete=models.CASCADE, verbose_name="Comprobante"
    )
    description = models.CharField(max_length=255, verbose_name="Descripción")
    quantity = models.PositiveIntegerField(verbose_name="Cantidad")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio unitario")
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Subtotal línea")

    class Meta:
        verbose_name = "Línea de comprobante"
        verbose_name_plural = "Líneas de comprobante"

    def __str__(self) -> str:
        return f"{self.quantity} x {self.description}"
