from rest_framework import generics, permissions

from apps.reservations.models import Reservation
from apps.reservations.serializers import ReservationSerializer


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.common.views import IsStaffOrAdmin

class ReservationListCreateView(generics.ListCreateAPIView):
    serializer_class = ReservationSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Reservation.objects.none()
        if self.request.user.role in ["admin", "staff"] or self.request.user.is_staff:
            return Reservation.objects.all().order_by("-reserved_at")
        return Reservation.objects.filter(user=self.request.user).order_by("-reserved_at")


class ReservationStatusUpdateView(APIView):
    """PATCH /api/reservations/{pk}/estado/ — cambiar estado (admin/staff)."""
    permission_classes = [IsStaffOrAdmin]

    def patch(self, request, pk):
        try:
            res = Reservation.objects.get(pk=pk)
        except Reservation.DoesNotExist:
            return Response({"detail": "Reserva no encontrada."}, status=status.HTTP_404_NOT_FOUND)

        new_status = request.data.get("status")
        if not new_status or new_status not in ["pending", "confirmed", "cancelled"]:
            return Response({"detail": "Estado inválido."}, status=status.HTTP_400_BAD_REQUEST)

        res.status = new_status
        res.save(update_fields=["status"])
        return Response(ReservationSerializer(res).data)
