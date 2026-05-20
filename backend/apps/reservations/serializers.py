from django.utils import timezone
from rest_framework import serializers

from apps.reservations.models import Reservation


class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = ("id", "customer_name", "customer_email", "customer_phone", "reserved_at", "party_size", "status", "notes", "created_at")
        read_only_fields = ("status", "created_at")

    def validate_reserved_at(self, value):
        if value <= timezone.now():
            raise serializers.ValidationError("La reserva debe ser para una fecha y hora futura.")
        return value

    def validate_party_size(self, value):
        if value < 1:
            raise serializers.ValidationError("La cantidad de personas debe ser al menos 1.")
        return value

    def create(self, validated_data):
        request = self.context["request"]
        if request.user.is_authenticated:
            validated_data["user"] = request.user
        return super().create(validated_data)
