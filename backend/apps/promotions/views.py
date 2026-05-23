from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.views import IsStaffOrAdmin
from apps.promotions.models import Promotion
from apps.promotions.serializers import PromotionSerializer, ValidateCodeSerializer


class PromotionListCreateView(generics.ListCreateAPIView):
    queryset = Promotion.objects.all()
    serializer_class = PromotionSerializer
    permission_classes = [IsStaffOrAdmin]


class PromotionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Promotion.objects.all()
    serializer_class = PromotionSerializer
    permission_classes = [IsStaffOrAdmin]


class ValidatePromotionCodeView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ValidateCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        promo = serializer.validated_data["promotion"]
        return Response(
            {
                "id": promo.id,
                "name": promo.name,
                "code": promo.code,
                "discount_type": promo.discount_type,
                "discount_value": str(promo.discount_value),
            }
        )
