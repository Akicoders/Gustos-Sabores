from django.urls import path

from apps.reservations.views import ReservationListCreateView

urlpatterns = [path("", ReservationListCreateView.as_view(), name="reservations")]
