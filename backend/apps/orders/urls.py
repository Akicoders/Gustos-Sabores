from django.urls import path

from apps.orders.views import AllOrdersView, OrderDetailView, OrderListCreateView, OrderStatusUpdateView

urlpatterns = [
    path("", OrderListCreateView.as_view(), name="pedidos"),
    path("todos/", AllOrdersView.as_view(), name="pedidos-todos"),
    path("<int:pk>/", OrderDetailView.as_view(), name="pedido-detalle"),
    path("<int:pk>/estado/", OrderStatusUpdateView.as_view(), name="pedido-estado"),
]
