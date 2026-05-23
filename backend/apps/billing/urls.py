from django.urls import path

from apps.billing.views import InvoiceDetailView, InvoiceListCreateView, InvoicePDFView

urlpatterns = [
    path("", InvoiceListCreateView.as_view(), name="comprobantes"),
    path("<int:pk>/", InvoiceDetailView.as_view(), name="comprobante-detalle"),
    path("<int:pk>/pdf/", InvoicePDFView.as_view(), name="comprobante-pdf"),
]
