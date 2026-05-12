from django.contrib import admin

from apps.reservations.models import Reservation


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ("id", "customer_name", "reserved_at", "party_size", "status")
    list_filter = ("status",)
    search_fields = ("customer_name", "customer_email", "customer_phone")
