from django.db.models import Count, Sum
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.menu.models import Category, Dish
from apps.orders.models import Order
from apps.reservations.models import Reservation


class DashboardKPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, _request):
        order_statuses = dict(Order.objects.values_list("status").annotate(total=Count("id")))
        reservation_statuses = dict(Reservation.objects.values_list("status").annotate(total=Count("id")))
        menu_by_category = dict(Category.objects.annotate(total=Count("dishes")).values_list("name", "total"))

        revenue = Order.objects.aggregate(total=Sum("total"))["total"] or 0

        return Response(
            {
                "orders_total": Order.objects.count(),
                "orders_revenue": revenue,
                "orders_by_status": order_statuses,
                "reservations_total": Reservation.objects.count(),
                "reservations_by_status": reservation_statuses,
                "dishes_total": Dish.objects.count(),
                "available_dishes": Dish.objects.filter(is_available=True).count(),
                "menu_by_category": menu_by_category,
            }
        )
