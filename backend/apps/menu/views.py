from django.db.models import Prefetch
from rest_framework import generics, permissions

from apps.common.views import IsStaffOrAdmin
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


# --- Vistas de administración ---

class DishAdminListCreateView(generics.ListCreateAPIView):
    """Admin: lista todos los platos (incluye no disponibles) y permite crear."""
    serializer_class = DishSerializer
    permission_classes = [IsStaffOrAdmin]

    def get_queryset(self):
        return Dish.objects.select_related("category").all()


class DishAdminDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Admin: editar y eliminar un plato."""
    queryset = Dish.objects.select_related("category").all()
    serializer_class = DishSerializer
    permission_classes = [IsStaffOrAdmin]


class CategoryAdminListCreateView(generics.ListCreateAPIView):
    """Admin: CRUD de categorías."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsStaffOrAdmin]


class CategoryAdminDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsStaffOrAdmin]
