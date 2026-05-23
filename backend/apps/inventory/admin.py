from django.contrib import admin

from apps.inventory.models import InventoryItem, StockMovement


@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ("name", "unit", "stock", "min_stock", "cost_price", "is_low_stock")
    search_fields = ("name",)
    list_filter = ("unit",)

    @admin.display(boolean=True, description="Stock bajo")
    def is_low_stock(self, obj):
        return obj.is_low_stock


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ("item", "movement_type", "quantity", "created_by", "created_at")
    list_filter = ("movement_type",)
    readonly_fields = ("created_at",)
