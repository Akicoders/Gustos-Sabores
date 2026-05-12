from rest_framework import generics, permissions

from apps.menu.models import Category, Dish
from apps.menu.serializers import CategorySerializer, DishSerializer


class CategoryListView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    queryset = Category.objects.prefetch_related("dishes").all()
    serializer_class = CategorySerializer


class DishListView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = DishSerializer

    def get_queryset(self):
        queryset = Dish.objects.select_related("category").all()
        category_slug = self.request.query_params.get("category")
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        return queryset
