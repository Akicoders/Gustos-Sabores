from django.contrib import admin

from apps.promotions.models import Promotion


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "discount_type", "discount_value", "starts_at", "ends_at", "is_active", "times_used")
    list_filter = ("is_active", "discount_type")
    search_fields = ("name", "code")
    readonly_fields = ("times_used", "created_at", "updated_at")
