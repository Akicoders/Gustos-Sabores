from rest_framework import serializers

from apps.suppliers.models import Supplier, SupplierProduct


class SupplierProductSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source="item.name", read_only=True)

    class Meta:
        model = SupplierProduct
        fields = ("id", "item", "item_name", "purchase_price", "is_preferred")


class SupplierSerializer(serializers.ModelSerializer):
    products = SupplierProductSerializer(many=True, read_only=True)

    class Meta:
        model = Supplier
        fields = (
            "id", "name", "ruc", "contact_name", "phone", "email",
            "address", "notes", "is_active", "products", "created_at",
        )
        read_only_fields = ("created_at",)
