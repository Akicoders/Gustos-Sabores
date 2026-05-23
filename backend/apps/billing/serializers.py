from decimal import Decimal

from rest_framework import serializers

from apps.billing.models import Invoice, InvoiceItem
from apps.orders.models import Order


class InvoiceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceItem
        fields = ("id", "description", "quantity", "unit_price", "subtotal")


class InvoiceSerializer(serializers.ModelSerializer):
    items = InvoiceItemSerializer(many=True, read_only=True)
    number = serializers.CharField(read_only=True)
    invoice_type_display = serializers.CharField(source="get_invoice_type_display", read_only=True)

    class Meta:
        model = Invoice
        fields = (
            "id",
            "number",
            "invoice_type",
            "invoice_type_display",
            "series",
            "correlative",
            "order",
            "receptor_name",
            "receptor_doc",
            "receptor_address",
            "receptor_email",
            "subtotal",
            "igv",
            "discount",
            "total",
            "issued_by",
            "items",
            "created_at",
        )
        read_only_fields = ("series", "correlative", "subtotal", "igv", "total", "issued_by", "created_at")


class CreateInvoiceSerializer(serializers.Serializer):
    """Crea una factura/boleta a partir de un pedido existente."""
    order_id = serializers.PrimaryKeyRelatedField(
        queryset=Order.objects.all(), source="order"
    )
    invoice_type = serializers.ChoiceField(
        choices=Invoice.InvoiceType.choices, default=Invoice.InvoiceType.BOLETA
    )
    receptor_name = serializers.CharField(max_length=255)
    receptor_doc = serializers.CharField(max_length=20, required=False, allow_blank=True, default="")
    receptor_address = serializers.CharField(max_length=255, required=False, allow_blank=True, default="")
    receptor_email = serializers.EmailField(required=False, allow_blank=True, default="")

    def validate_order_id(self, order):
        if hasattr(order, "invoice"):
            raise serializers.ValidationError("Este pedido ya tiene un comprobante emitido.")
        return order

    def create(self, validated_data):
        request = self.context.get("request")
        order: Order = validated_data["order"]

        # Calcular montos: total del pedido incluye IGV
        IGV_RATE = Decimal("0.18")
        total_with_igv = order.total
        discount = order.discount_amount if hasattr(order, "discount_amount") else Decimal("0.00")
        base = (total_with_igv / (1 + IGV_RATE)).quantize(Decimal("0.01"))
        igv = (total_with_igv - base).quantize(Decimal("0.01"))

        # Correlativo automático
        last = Invoice.objects.order_by("-correlative").first()
        correlative = (last.correlative + 1) if last else 1

        invoice = Invoice.objects.create(
            order=order,
            invoice_type=validated_data["invoice_type"],
            correlative=correlative,
            receptor_name=validated_data["receptor_name"],
            receptor_doc=validated_data.get("receptor_doc", ""),
            receptor_address=validated_data.get("receptor_address", ""),
            receptor_email=validated_data.get("receptor_email", ""),
            subtotal=base,
            igv=igv,
            discount=discount,
            total=total_with_igv,
            issued_by=request.user if request and request.user.is_authenticated else None,
        )

        # Crear líneas de detalle desde los ítems del pedido
        for item in order.items.select_related("dish").all():
            line_subtotal = (item.unit_price * item.quantity).quantize(Decimal("0.01"))
            InvoiceItem.objects.create(
                invoice=invoice,
                description=item.dish.name,
                quantity=item.quantity,
                unit_price=item.unit_price,
                subtotal=line_subtotal,
            )

        return invoice
