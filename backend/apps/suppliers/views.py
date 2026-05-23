from rest_framework import generics

from apps.common.views import IsStaffOrAdmin
from apps.suppliers.models import Supplier
from apps.suppliers.serializers import SupplierSerializer


class SupplierListCreateView(generics.ListCreateAPIView):
    queryset = Supplier.objects.prefetch_related("products__item").all()
    serializer_class = SupplierSerializer
    permission_classes = [IsStaffOrAdmin]


class SupplierDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Supplier.objects.prefetch_related("products__item").all()
    serializer_class = SupplierSerializer
    permission_classes = [IsStaffOrAdmin]
