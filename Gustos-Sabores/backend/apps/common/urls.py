from django.urls import path

from apps.common.views import DashboardKPIView

urlpatterns = [
    path("kpis/", DashboardKPIView.as_view(), name="dashboard-kpis"),
]
