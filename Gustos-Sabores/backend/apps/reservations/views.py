from rest_framework import generics, permissions

from apps.reservations.models import Reservation
from apps.reservations.serializers import ReservationSerializer


class ReservationListCreateView(generics.ListCreateAPIView):
    serializer_class = ReservationSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Reservation.objects.none()
        return Reservation.objects.filter(user=self.request.user)
