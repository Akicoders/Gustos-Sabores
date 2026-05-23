from rest_framework import serializers

from apps.inventory.models import InventoryItem, StockMovement


class InventoryItemSerializer(serializers.ModelSerializer):
    is_low_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = InventoryItem
        fields = (
            "id",
            "name",
            "unit",
            "stock",
            "min_stock",
            "cost_price",
            "notes",
            "is_low_stock",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("created_at", "updated_at")


class StockMovementSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source="item.name", read_only=True)
    created_by_name = serializers.CharField(source="created_by.full_name", read_only=True, default="")

    class Meta:
        model = StockMovement
        fields = (
            "id",
            "item",
            "item_name",
            "movement_type",
            "quantity",
            "notes",
            "created_by",
            "created_by_name",
            "created_at",
        )
        read_only_fields = ("created_by", "created_at")

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("La cantidad debe ser mayor a cero.")
        return value

    def create(self, validated_data):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            validated_data["created_by"] = request.user
        return super().create(validated_data)
