from django.urls import path

from apps.menu.views import CategoryListView, DishListView

urlpatterns = [
    path("categories/", CategoryListView.as_view(), name="menu-categories"),
    path("dishes/", DishListView.as_view(), name="menu-dishes"),
]
