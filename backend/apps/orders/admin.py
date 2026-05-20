from django.contrib import admin

from apps.orders.models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "customer_name", "order_type", "payment_method", "status", "total", "created_at")
    list_filter = ("status", "order_type", "payment_method")
    search_fields = ("customer_name", "customer_email", "customer_phone")
    inlines = [OrderItemInline]
