import io
from decimal import Decimal

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable

from apps.billing.models import Invoice

# Colores de la paleta del restaurante
JADE = colors.HexColor("#003f35")
JADE_2 = colors.HexColor("#005648")
ACCENT = colors.HexColor("#e3962e")
CREAM = colors.HexColor("#f7f3e9")
INK_SOFT = colors.HexColor("#4e6862")


def generate_invoice_pdf(invoice: Invoice) -> bytes:
    """Genera el PDF de un comprobante y retorna los bytes."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "title",
        parent=styles["Heading1"],
        textColor=JADE,
        fontSize=20,
        spaceAfter=4,
        fontName="Helvetica-Bold",
    )
    subtitle_style = ParagraphStyle(
        "subtitle",
        parent=styles["Normal"],
        textColor=INK_SOFT,
        fontSize=10,
        spaceAfter=2,
    )
    label_style = ParagraphStyle(
        "label",
        parent=styles["Normal"],
        textColor=JADE_2,
        fontSize=9,
        fontName="Helvetica-Bold",
    )
    value_style = ParagraphStyle(
        "value",
        parent=styles["Normal"],
        fontSize=9,
    )

    story = []

    # — Encabezado —
    story.append(Paragraph("Gustos y Sabores", title_style))
    story.append(Paragraph("Cocina auténtica tradicional", subtitle_style))
    story.append(Spacer(1, 0.3 * cm))
    story.append(HRFlowable(width="100%", thickness=2, color=JADE))
    story.append(Spacer(1, 0.3 * cm))

    # Tipo de comprobante y número
    story.append(Paragraph(invoice.get_invoice_type_display().upper(), title_style))
    story.append(Paragraph(f"N° {invoice.number}", subtitle_style))
    story.append(Paragraph(f"Fecha de emisión: {invoice.created_at.strftime('%d/%m/%Y %H:%M')}", subtitle_style))
    story.append(Spacer(1, 0.4 * cm))

    # — Datos del receptor —
    receptor_data = [
        [Paragraph("Cliente:", label_style), Paragraph(invoice.receptor_name, value_style)],
        [Paragraph("DNI / RUC:", label_style), Paragraph(invoice.receptor_doc or "—", value_style)],
        [Paragraph("Dirección:", label_style), Paragraph(invoice.receptor_address or "—", value_style)],
        [Paragraph("Correo:", label_style), Paragraph(invoice.receptor_email or "—", value_style)],
    ]
    receptor_table = Table(receptor_data, colWidths=[4 * cm, None])
    receptor_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(receptor_table)
    story.append(Spacer(1, 0.5 * cm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=INK_SOFT))
    story.append(Spacer(1, 0.4 * cm))

    # — Detalle de ítems —
    header = ["Descripción", "Cant.", "P. Unitario", "Subtotal"]
    rows = [header]
    for item in invoice.items.all():
        rows.append([
            item.description,
            str(item.quantity),
            f"S/ {item.unit_price:.2f}",
            f"S/ {item.subtotal:.2f}",
        ])

    items_table = Table(rows, colWidths=[None, 2 * cm, 3.5 * cm, 3.5 * cm])
    items_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), JADE),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [CREAM, colors.white]),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("GRID", (0, 0), (-1, -1), 0.3, INK_SOFT),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(items_table)
    story.append(Spacer(1, 0.5 * cm))

    # — Totales —
    totals_data = [
        ["Subtotal (sin IGV):", f"S/ {invoice.subtotal:.2f}"],
        ["IGV (18%):", f"S/ {invoice.igv:.2f}"],
    ]
    if invoice.discount > 0:
        totals_data.append(["Descuento:", f"- S/ {invoice.discount:.2f}"])
    totals_data.append(["TOTAL:", f"S/ {invoice.total:.2f}"])

    totals_table = Table(totals_data, colWidths=[None, 3.5 * cm], hAlign="RIGHT")
    totals_table.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("TEXTCOLOR", (0, -1), (-1, -1), JADE),
        ("FONTSIZE", (0, -1), (-1, -1), 11),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LINEABOVE", (0, -1), (-1, -1), 1, JADE),
    ]))
    story.append(totals_table)
    story.append(Spacer(1, 1 * cm))

    # — Pie —
    story.append(HRFlowable(width="100%", thickness=1, color=JADE))
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph(
        "Gracias por su preferencia · Gustos y Sabores",
        ParagraphStyle("footer", parent=styles["Normal"], textColor=INK_SOFT, fontSize=8, alignment=1),
    ))

    doc.build(story)
    return buffer.getvalue()
