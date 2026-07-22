from rest_framework import serializers
from .models import Complaint, ActivityLog


class ComplaintSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Complaint
        fields = ['id', 'name', 'email', 'phone', 'subject', 'description', 'status', 'status_display', 'response', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'status_display', 'status', 'response']


class ActivityLogSerializer(serializers.ModelSerializer):
    action_display = serializers.CharField(source='get_action_display', read_only=True)

    class Meta:
        model = ActivityLog
        fields = ['id', 'action', 'action_display', 'user_email', 'resource_type', 'resource_id', 'details', 'ip_address', 'created_at']
        read_only_fields = ['id', 'created_at', 'action_display']
