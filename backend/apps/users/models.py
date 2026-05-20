from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.common.models import TimeStampedModel


class User(AbstractUser, TimeStampedModel):
    REQUIRED_FIELDS = ["email", "full_name"]

    class Roles(models.TextChoices):
        CUSTOMER = "customer", "Cliente"
        STAFF = "staff", "Personal"
        ADMIN = "admin", "Administrador"

    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=30, blank=True)
    address = models.CharField(max_length=255, blank=True)
    role = models.CharField(max_length=20, choices=Roles.choices, default=Roles.CUSTOMER)

    def __str__(self) -> str:
        return self.full_name or self.username
