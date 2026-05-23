from rest_framework import generics, permissions, serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.views import IsStaffOrAdmin
from apps.orders.models import Order
from apps.orders.serializers import OrderSerializer


class OrderListCreateView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Order.objects.none()
        return Order.objects.prefetch_related("items__dish").filter(user=self.request.user)


class AllOrdersView(generics.ListAPIView):
    """Vista de administrador: todos los pedidos con filtro por estado."""
    serializer_class = OrderSerializer
    permission_classes = [IsStaffOrAdmin]

    def get_queryset(self):
        qs = Order.objects.prefetch_related("items__dish").select_related("promotion").order_by("-created_at")
        estado = self.request.query_params.get("estado")
        if estado:
            qs = qs.filter(status=estado)
        return qs


class OrderStatusUpdateView(APIView):
    """PATCH /api/orders/{pk}/estado/ — solo staff/admin."""
    permission_classes = [IsStaffOrAdmin]

    VALID_TRANSITIONS = {
        Order.Status.PENDING: [Order.Status.PREPARING, Order.Status.CANCELLED],
        Order.Status.PREPARING: [Order.Status.READY, Order.Status.CANCELLED],
        Order.Status.READY: [Order.Status.DELIVERED],
        Order.Status.DELIVERED: [],
        Order.Status.CANCELLED: [],
    }

    def patch(self, request, pk):
        try:
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return Response({"detail": "Pedido no encontrado."}, status=status.HTTP_404_NOT_FOUND)

        new_status = request.data.get("status")
        if not new_status:
            return Response({"detail": "El campo 'status' es requerido."}, status=status.HTTP_400_BAD_REQUEST)

        allowed = self.VALID_TRANSITIONS.get(order.status, [])
        if new_status not in allowed:
            return Response(
                {"detail": f"Transición inválida: de '{order.status}' a '{new_status}'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        order.status = new_status
        order.save(update_fields=["status"])
        return Response(OrderSerializer(order).data)
