from django.http import HttpResponse
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.billing.models import Invoice
from apps.billing.serializers import CreateInvoiceSerializer, InvoiceSerializer
from apps.billing.utils import generate_invoice_pdf
from apps.common.views import IsStaffOrAdmin


class InvoiceListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsStaffOrAdmin]

    def get_queryset(self):
        return Invoice.objects.select_related("order", "issued_by").prefetch_related("items").all()

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CreateInvoiceSerializer
        return InvoiceSerializer

    def create(self, request, *args, **kwargs):
        serializer = CreateInvoiceSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        invoice = serializer.save()
        return Response(InvoiceSerializer(invoice).data, status=status.HTTP_201_CREATED)


class InvoiceDetailView(generics.RetrieveAPIView):
    queryset = Invoice.objects.select_related("order", "issued_by").prefetch_related("items").all()
    serializer_class = InvoiceSerializer
    permission_classes = [IsStaffOrAdmin]


class InvoicePDFView(APIView):
    permission_classes = [IsStaffOrAdmin]

    def get(self, request, pk):
        try:
            invoice = Invoice.objects.prefetch_related("items").get(pk=pk)
        except Invoice.DoesNotExist:
            return Response({"detail": "Comprobante no encontrado."}, status=status.HTTP_404_NOT_FOUND)

        pdf_bytes = generate_invoice_pdf(invoice)
        filename = f"comprobante-{invoice.number}.pdf"
        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response
