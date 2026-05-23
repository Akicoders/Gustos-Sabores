from django.contrib import admin

from apps.billing.models import Invoice, InvoiceItem


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 0
    readonly_fields = ("description", "quantity", "unit_price", "subtotal")


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("number", "invoice_type", "receptor_name", "total", "issued_by", "created_at")
    list_filter = ("invoice_type",)
    search_fields = ("receptor_name", "receptor_doc")
    readonly_fields = ("series", "correlative", "subtotal", "igv", "total", "issued_by", "created_at", "updated_at")
    inlines = [InvoiceItemInline]
