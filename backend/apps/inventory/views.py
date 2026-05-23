from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.views import IsStaffOrAdmin
from apps.inventory.models import InventoryItem, StockMovement
from apps.inventory.serializers import InventoryItemSerializer, StockMovementSerializer


class InventoryItemListCreateView(generics.ListCreateAPIView):
    queryset = InventoryItem.objects.all()
    serializer_class = InventoryItemSerializer
    permission_classes = [IsStaffOrAdmin]

    def get_queryset(self):
        qs = super().get_queryset()
        only_low = self.request.query_params.get("bajo_stock")
        if only_low == "1":
            # Filtra artículos cuyo stock <= min_stock en Python
            ids = [item.id for item in qs if item.is_low_stock]
            return qs.filter(id__in=ids)
        return qs


class InventoryItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = InventoryItem.objects.all()
    serializer_class = InventoryItemSerializer
    permission_classes = [IsStaffOrAdmin]


class StockMovementListCreateView(generics.ListCreateAPIView):
    serializer_class = StockMovementSerializer
    permission_classes = [IsStaffOrAdmin]

    def get_queryset(self):
        item_id = self.kwargs.get("item_id")
        return StockMovement.objects.filter(item_id=item_id).select_related("item", "created_by")

    def perform_create(self, serializer):
        item_id = self.kwargs.get("item_id")
        serializer.save(item_id=item_id)
