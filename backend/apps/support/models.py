from django.db import models
from apps.common.models import TimeStampedModel


class Complaint(TimeStampedModel):
    STATUS_CHOICES = (
        ('new', 'Nueva'),
        ('in_progress', 'En progreso'),
        ('resolved', 'Resuelta'),
        ('closed', 'Cerrada'),
    )

    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    subject = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    response = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Reclamación'
        verbose_name_plural = 'Reclamaciones'

    def __str__(self):
        return f"{self.subject} - {self.name} ({self.get_status_display()})"


class ActivityLog(TimeStampedModel):
    ACTION_CHOICES = (
        ('order_created', 'Orden creada'),
        ('order_updated', 'Orden actualizada'),
        ('order_completed', 'Orden completada'),
        ('reservation_created', 'Reserva creada'),
        ('reservation_updated', 'Reserva actualizada'),
        ('reservation_cancelled', 'Reserva cancelada'),
        ('login', 'Acceso'),
        ('logout', 'Cierre de sesión'),
        ('admin_action', 'Acción de admin'),
    )

    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    user_email = models.EmailField(blank=True, default='')
    resource_type = models.CharField(max_length=50, blank=True, default='')
    resource_id = models.IntegerField(blank=True, null=True)
    details = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Registro de actividad'
        verbose_name_plural = 'Registros de actividad'
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['action']),
        ]

    def __str__(self):
        return f"{self.get_action_display()} - {self.created_at}"
