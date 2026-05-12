from decimal import Decimal

from django.db import transaction
from rest_framework import serializers

from apps.menu.models import Dish
from apps.orders.models import Order, OrderItem


class OrderItemReadSerializer(serializers.ModelSerializer):
    dish = serializers.StringRelatedField()

    class Meta:
        model = OrderItem
        fields = ("id", "dish", "quantity", "unit_price")


class OrderItemWriteSerializer(serializers.Serializer):
    dish_id = serializers.PrimaryKeyRelatedField(queryset=Dish.objects.filter(is_available=True), source="dish")
    quantity = serializers.IntegerField(min_value=1)


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemWriteSerializer(many=True, write_only=True)
    item_details = OrderItemReadSerializer(many=True, source="items", read_only=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "customer_name",
            "customer_email",
            "customer_phone",
            "delivery_address",
            "order_type",
            "payment_method",
            "status",
            "notes",
            "total",
            "items",
            "item_details",
            "created_at",
        )
        read_only_fields = ("status", "total", "created_at")

    def validate(self, attrs):
        if attrs.get("order_type") == Order.OrderType.DELIVERY and not attrs.get("delivery_address"):
            raise serializers.ValidationError({"delivery_address": "La direccion es obligatoria para delivery."})
        return attrs

    def create(self, validated_data):
        with transaction.atomic():
            items_data = validated_data.pop("items")
            request = self.context["request"]
            if request.user.is_authenticated:
                validated_data["user"] = request.user

            order = Order.objects.create(**validated_data)
            total = Decimal("0.00")
            for item in items_data:
                dish = item["dish"]
                quantity = item["quantity"]
                OrderItem.objects.create(order=order, dish=dish, quantity=quantity, unit_price=dish.price)
                total += dish.price * quantity

            order.total = total
            order.save(update_fields=["total"])
            return order
