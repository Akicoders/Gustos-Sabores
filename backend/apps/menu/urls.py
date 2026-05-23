from django.urls import path

from apps.menu.views import (
    CategoryAdminDetailView,
    CategoryAdminListCreateView,
    CategoryListView,
    DishAdminDetailView,
    DishAdminListCreateView,
    DishListView,
)

urlpatterns = [
    # Públicas
    path("categories/", CategoryListView.as_view(), name="menu-categorias"),
    path("dishes/", DishListView.as_view(), name="menu-platos"),
    # Admin
    path("admin/dishes/", DishAdminListCreateView.as_view(), name="admin-platos"),
    path("admin/dishes/<int:pk>/", DishAdminDetailView.as_view(), name="admin-plato-detalle"),
    path("admin/categories/", CategoryAdminListCreateView.as_view(), name="admin-categorias"),
    path("admin/categories/<int:pk>/", CategoryAdminDetailView.as_view(), name="admin-categoria-detalle"),
]
