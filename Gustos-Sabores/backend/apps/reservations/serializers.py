from rest_framework import serializers

from apps.reservations.models import Reservation


class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = ("id", "customer_name", "customer_email", "customer_phone", "reserved_at", "party_size", "status", "notes", "created_at")
        read_only_fields = ("status", "created_at")

    def create(self, validated_data):
        request = self.context["request"]
        if request.user.is_authenticated:
            validated_data["user"] = request.user
        return super().create(validated_data)
