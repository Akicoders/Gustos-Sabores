from django.utils import timezone
from rest_framework import serializers

from apps.promotions.models import Promotion


class PromotionSerializer(serializers.ModelSerializer):
    is_valid = serializers.SerializerMethodField()

    class Meta:
        model = Promotion
        fields = (
            "id",
            "name",
            "description",
            "code",
            "discount_type",
            "discount_value",
            "min_order_amount",
            "starts_at",
            "ends_at",
            "is_active",
            "usage_limit",
            "times_used",
            "is_valid",
            "created_at",
        )
        read_only_fields = ("times_used", "created_at")

    def get_is_valid(self, obj) -> bool:
        return obj.is_valid()

    def validate(self, attrs):
        if attrs.get("ends_at") and attrs.get("starts_at"):
            if attrs["ends_at"] <= attrs["starts_at"]:
                raise serializers.ValidationError(
                    {"ends_at": "La fecha de fin debe ser posterior a la de inicio."}
                )
        return attrs


class ValidateCodeSerializer(serializers.Serializer):
    code = serializers.CharField()
    order_amount = serializers.DecimalField(max_digits=10, decimal_places=2)

    def validate(self, attrs):
        code = attrs["code"].strip().upper()
        try:
            promo = Promotion.objects.get(code__iexact=code)
        except Promotion.DoesNotExist:
            raise serializers.ValidationError({"code": "Código de promoción inválido."})

        if not promo.is_valid():
            raise serializers.ValidationError({"code": "Esta promoción ya no está activa o expiró."})

        if attrs["order_amount"] < promo.min_order_amount:
            raise serializers.ValidationError(
                {
                    "code": f"El pedido mínimo para esta promoción es S/ {promo.min_order_amount}."
                }
            )

        attrs["promotion"] = promo
        return attrs
