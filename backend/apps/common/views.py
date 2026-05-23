from datetime import timedelta
from django.db.models import Count, Sum
from django.utils import timezone
from rest_framework.permissions import BasePermission
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.menu.models import Category, Dish
from apps.orders.models import Order
from apps.reservations.models import Reservation


class IsStaffOrAdmin(BasePermission):
    def has_permission(self, request, _view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and (user.is_staff or getattr(user, "role", None) in {"staff", "admin"})
        )


class DashboardKPIView(APIView):
    permission_classes = [IsStaffOrAdmin]

    def get(self, _request):
        order_statuses = dict(Order.objects.values_list("status").annotate(total=Count("id")))
        reservation_statuses = dict(Reservation.objects.values_list("status").annotate(total=Count("id")))
        menu_by_category = dict(Category.objects.annotate(total=Count("dishes")).values_list("name", "total"))

        revenue = Order.objects.aggregate(total=Sum("total"))["total"] or 0

        # 1. Calcular tendencia de ingresos de los últimos 7 días calendario
        today = timezone.localtime(timezone.now()).date()
        revenue_trend = []
        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            day_start = timezone.make_aware(timezone.datetime.combine(day, timezone.datetime.min.time()))
            day_end = timezone.make_aware(timezone.datetime.combine(day, timezone.datetime.max.time()))
            
            day_revenue = Order.objects.filter(
                created_at__range=(day_start, day_end)
            ).exclude(
                status="cancelled"
            ).aggregate(total=Sum("total"))["total"] or 0
            
            revenue_trend.append({
                "date": day.strftime("%Y-%m-%d"),
                "day_name": ["Dom", "Lun", "Mar", "Mié", "Jue", "Vie", "Sáb"][day.weekday()],
                "revenue": float(day_revenue)
            })

        # 2. Distribución de tipos de pedido (Local vs Delivery)
        order_types = dict(Order.objects.values_list("order_type").annotate(total=Count("id")))

        # 3. Actividad reciente combinada (últimos 5)
        recent_orders = Order.objects.all().order_by("-created_at")[:5]
        recent_reservations = Reservation.objects.all().order_by("-created_at")[:5]

        recent_activities = []
        for o in recent_orders:
            recent_activities.append({
                "type": "order",
                "id": o.id,
                "title": f"Pedido #{o.id}",
                "description": f"{o.customer_name} ({o.get_order_type_display()})",
                "meta": f"S/ {o.total}",
                "status": o.status,
                "timestamp": o.created_at.isoformat()
            })
        for r in recent_reservations:
            recent_activities.append({
                "type": "reservation",
                "id": r.id,
                "title": f"Reserva #{r.id}",
                "description": f"{r.customer_name} - {r.party_size} pers.",
                "meta": r.reserved_at.strftime("%H:%M"),
                "status": r.status,
                "timestamp": r.created_at.isoformat()
            })

        recent_activities.sort(key=lambda x: x["timestamp"], reverse=True)
        recent_activities = recent_activities[:5]

        return Response(
            {
                "orders_total": Order.objects.count(),
                "orders_revenue": float(revenue),
                "orders_by_status": order_statuses,
                "reservations_total": Reservation.objects.count(),
                "reservations_by_status": reservation_statuses,
                "dishes_total": Dish.objects.count(),
                "available_dishes": Dish.objects.filter(is_available=True).count(),
                "menu_by_category": menu_by_category,
                "revenue_trend": revenue_trend,
                "order_types": order_types,
                "recent_activity": recent_activities,
            }
        )
