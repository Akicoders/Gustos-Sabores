from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path


def health_view(_request):
    return JsonResponse({"status": "ok", "service": "gustos-sabores-api"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", health_view, name="health"),
    path("api/dashboard/", include("apps.common.urls")),
    path("api/auth/", include("apps.users.urls")),
    path("api/menu/", include("apps.menu.urls")),
    path("api/orders/", include("apps.orders.urls")),
    path("api/reservations/", include("apps.reservations.urls")),
]
