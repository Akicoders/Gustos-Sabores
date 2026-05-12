from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from apps.users.models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Perfil", {"fields": ("full_name", "phone", "address", "role")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Perfil", {"fields": ("full_name", "email", "phone", "address", "role")}),
    )
    list_display = ("username", "email", "full_name", "role", "is_staff")
    search_fields = ("username", "email", "full_name")
