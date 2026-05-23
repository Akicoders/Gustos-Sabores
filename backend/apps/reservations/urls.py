from django.urls import path

from apps.reservations.views import ReservationListCreateView, ReservationStatusUpdateView

urlpatterns = [
    path("", ReservationListCreateView.as_view(), name="reservations"),
    path("<int:pk>/estado/", ReservationStatusUpdateView.as_view(), name="reservation-estado"),
]
