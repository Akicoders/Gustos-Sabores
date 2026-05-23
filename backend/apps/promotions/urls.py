from django.urls import path

from apps.promotions.views import PromotionDetailView, PromotionListCreateView, ValidatePromotionCodeView

urlpatterns = [
    path("", PromotionListCreateView.as_view(), name="promociones"),
    path("<int:pk>/", PromotionDetailView.as_view(), name="promocion-detalle"),
    path("validar/", ValidatePromotionCodeView.as_view(), name="validar-codigo"),
]
