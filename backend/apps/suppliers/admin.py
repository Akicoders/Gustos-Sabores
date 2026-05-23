from django.contrib import admin

from apps.suppliers.models import Supplier, SupplierProduct


class SupplierProductInline(admin.TabularInline):
    model = SupplierProduct
    extra = 1


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ("name", "ruc", "contact_name", "phone", "email", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "ruc", "contact_name")
    inlines = [SupplierProductInline]
