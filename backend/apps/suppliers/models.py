from django.db import models

from apps.common.models import TimeStampedModel
from apps.inventory.models import InventoryItem


class Supplier(TimeStampedModel):
    name = models.CharField(max_length=200, verbose_name="Razón social / Nombre")
    ruc = models.CharField(max_length=11, blank=True, verbose_name="RUC")
    contact_name = models.CharField(max_length=200, blank=True, verbose_name="Contacto")
    phone = models.CharField(max_length=30, blank=True, verbose_name="Teléfono")
    email = models.EmailField(blank=True, verbose_name="Correo")
    address = models.CharField(max_length=255, blank=True, verbose_name="Dirección")
    notes = models.TextField(blank=True, verbose_name="Notas")
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name


class SupplierProduct(TimeStampedModel):
    supplier = models.ForeignKey(
        Supplier,
        related_name="products",
        on_delete=models.CASCADE,
        verbose_name="Proveedor",
    )
    item = models.ForeignKey(
        InventoryItem,
        related_name="supplier_products",
        on_delete=models.CASCADE,
        verbose_name="Artículo de inventario",
    )
    purchase_price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Precio de compra"
    )
    is_preferred = models.BooleanField(default=False, verbose_name="Proveedor preferido")

    class Meta:
        verbose_name = "Producto de proveedor"
        verbose_name_plural = "Productos de proveedor"
        unique_together = ("supplier", "item")

    def __str__(self) -> str:
        return f"{self.supplier.name} → {self.item.name}"
