from django.db.models import Prefetch
from rest_framework import generics, permissions

from apps.menu.models import Category, Dish
from apps.menu.serializers import CategorySerializer, DishSerializer


class CategoryListView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = CategorySerializer

    def get_queryset(self):
        available_dishes = Dish.objects.filter(is_available=True).select_related("category")
        return (
            Category.objects.filter(dishes__is_available=True)
            .distinct()
            .prefetch_related(Prefetch("dishes", queryset=available_dishes))
        )


class DishListView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = DishSerializer

    def get_queryset(self):
        queryset = Dish.objects.select_related("category").filter(is_available=True)
        category_slug = self.request.query_params.get("category")
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        return queryset
