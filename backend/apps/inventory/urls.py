from django.urls import path

from apps.inventory.views import InventoryItemDetailView, InventoryItemListCreateView, StockMovementListCreateView

urlpatterns = [
    path("", InventoryItemListCreateView.as_view(), name="inventario"),
    path("<int:pk>/", InventoryItemDetailView.as_view(), name="inventario-detalle"),
    path("<int:item_id>/movimientos/", StockMovementListCreateView.as_view(), name="stock-movimientos"),
]
