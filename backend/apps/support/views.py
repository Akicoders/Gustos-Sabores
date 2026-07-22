from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from django.utils.timezone import timedelta
from django.utils import timezone
from .models import Complaint, ActivityLog
from .serializers import ComplaintSerializer, ActivityLogSerializer


class ComplaintViewSet(viewsets.ModelViewSet):
    queryset = Complaint.objects.all()
    serializer_class = ComplaintSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return [IsAdminUser()]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            {'detail': 'Reclamación enviada exitosamente. Nos pondremos en contacto pronto.'},
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def resolve(self, request, pk=None):
        complaint = self.get_object()
        complaint.status = 'resolved'
        complaint.response = request.data.get('response', '')
        complaint.save()
        return Response(ComplaintSerializer(complaint).data)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def close(self, request, pk=None):
        complaint = self.get_object()
        complaint.status = 'closed'
        complaint.save()
        return Response(ComplaintSerializer(complaint).data)


class ActivityLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ActivityLog.objects.all()
    serializer_class = ActivityLogSerializer
    permission_classes = [IsAdminUser]
    filterset_fields = ['action', 'user_email', 'resource_type']
    ordering = ['-created_at']

    @action(detail=False, methods=['get'])
    def recent(self, request):
        days = int(request.query_params.get('days', 7))
        since = timezone.now() - timedelta(days=days)
        logs = ActivityLog.objects.filter(created_at__gte=since)
        serializer = self.get_serializer(logs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        days = int(request.query_params.get('days', 7))
        since = timezone.now() - timedelta(days=days)
        summary = {}
        for action, label in ActivityLog.ACTION_CHOICES:
            count = ActivityLog.objects.filter(action=action, created_at__gte=since).count()
            summary[action] = {'label': label, 'count': count}
        return Response(summary)
