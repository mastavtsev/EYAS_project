import base64
import os
import asyncio
from io import BytesIO

from fastapi import FastAPI, Response
from starlette.middleware.cors import CORSMiddleware
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image as PlatypusImage, Table, TableStyle, PageBreak
)
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from PIL import Image

from report_client import AuthenticatedClient
from report_client.api.default import get_report_image_api_v1_report_report_id_image_image_type_get
from whitebox.auth import create_service_token, CurrentServiceData
from whitebox.service import Service
from model_lib.utils import logger
from names_lib.names import VALUE_MAPPING
from models.report_models import ReportImageType

from .dtos import PDFInDTO, PDFOutDTO

app = FastAPI(title='pdf')
if os.environ.get("DISABLE_CORS"):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

report_client = AuthenticatedClient(
    os.environ.get("REPORT_SERVICE_URL"),
    create_service_token(Service.PDF)
)

pdfmetrics.registerFont(TTFont('DejaVu', 'DejaVuSans.ttf'))

styles = getSampleStyleSheet()
for style in styles.byName.values():
    style.fontName = 'DejaVu'

title_style = ParagraphStyle(
    name='TitleStyle',
    parent=styles['Heading1'],
    fontSize=18,
    textColor='#2d61d6'
)

h2_style = ParagraphStyle(
    name='H2Style',
    parent=styles['Heading2'],
    fontSize=14,
    textColor='#2d61d6'
)

h3_style = ParagraphStyle(
    name='H3Style',
    parent=styles['Heading3'],
    fontSize=12,
    textColor='#2d61d6'
)

normal_style = ParagraphStyle(
    name='NormalStyle',
    parent=styles['Normal'],
    fontSize=13
)

report_text_style = ParagraphStyle(
    'ReportText',
    parent=normal_style,
    backColor='#f5f7fa',
    borderPadding=10,
    borderLeftColor='#2d61d6',
    borderLeftWidth=4,
    leading=14
)


def render(elements, title, image_buffer, table_data):
    img = PlatypusImage(image_buffer)
    img.drawHeight = 90 * mm
    img.drawWidth = 90 * mm

    text_table = Table(table_data, colWidths=100 * mm)
    text_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0)
    ]))

    section_table = Table([[img, text_table]], colWidths=[100 * mm, 100 * mm])
    section_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (1, 0), (1, 0), 20),
    ]))

    elements.append(Paragraph(title, h2_style))
    elements.append(Spacer(1, 6))
    elements.append(section_table)
    elements.append(Spacer(1, 12))


def add_OD(elements, title, image_buffer, params):
    if not image_buffer:
        return

    table_data = []

    table_data.append([
        Paragraph(f'<b><font color="#2d61d6">Цвет:</font></b> {VALUE_MAPPING[params["od_color"]]}', normal_style)
    ])

    table_data.append([
        Paragraph(f'<b><font color="#2d61d6">Монотонность:</font></b> {params["od_monotone"]}',
                  normal_style)
    ])

    table_data.append([
        Paragraph(f'<b><font color="#2d61d6">Размер:</font></b> {VALUE_MAPPING[params["od_size"]]}', normal_style)
    ])

    table_data.append([
        Paragraph(f'<b><font color="#2d61d6">Форма:</font></b> {VALUE_MAPPING[params["od_shape"]]}', normal_style)
    ])

    table_data.append([
        Paragraph(f'<b><font color="#2d61d6">Границы:</font></b> {VALUE_MAPPING[params["od_border"]]}', normal_style)
    ])

    table_data.append([
        Paragraph(f'<b><font color="#808080">Экскавация:</font></b>', h3_style)
    ])

    table_data.append([
        Paragraph(f'<b><font color="#2d61d6">Размер:</font></b> {params["od_excavation_size"]}',
                  normal_style)
    ])

    table_data.append([
        Paragraph(f'<b><font color="#2d61d6">Сектор:</font></b> {VALUE_MAPPING[params["od_excavation_location"]]}',
                  normal_style)
    ])

    table_data.append([
        Paragraph(f'<b><font color="#2d61d6">Э/Д:</font></b> {params["od_excavation_ratio"]}',
                  normal_style)
    ])

    table_data.append([
        Paragraph(
            f'<b><font color="#2d61d6">Сосудистый пучок:</font></b> {VALUE_MAPPING[params["od_vessels_location"]]}',
            normal_style)
    ])

    table_data.append([
        Paragraph(f'<b><font color="#2d61d6">Патология:</font></b> {params["od_pathology"]}', normal_style)
    ])

    render(elements, title, image_buffer, table_data)


def add_vessels(elements, title, image_buffer, params):
    if not image_buffer:
        return

    table_data = []

    table_data.append([
        Paragraph(f'<b><font color="#808080">Артерии:</font></b>', h3_style)
    ])

    table_data.append([
        Paragraph(f'<b><font color="#2d61d6">Ход:</font></b> {VALUE_MAPPING[params["vessels_art_course"]]}',
                  normal_style)
    ])

    table_data.append([
        Paragraph(f'<b><font color="#2d61d6">Извитость:</font></b> {VALUE_MAPPING[params["vessels_art_turtuosity"]]}',
                  normal_style)
    ])

    table_data.append([
        Paragraph(f'<b><font color="#2d61d6">Бифуркация:</font></b> {VALUE_MAPPING[params["vessels_art_bifurcation"]]}',
                  normal_style)
    ])

    table_data.append([
        Paragraph(f'<b><font color="#2d61d6">Калибр:</font></b> {VALUE_MAPPING[params["vessels_art_caliber"]]}',
                  normal_style)
    ])

    table_data.append([
        Paragraph(f'<b><font color="#808080">Вены:</font></b>', h3_style)
    ])

    table_data.append([
        Paragraph(f'<b><font color="#2d61d6">Ход:</font></b> {VALUE_MAPPING[params["vessels_vein_course"]]}',
                  normal_style)
    ])

    table_data.append([
        Paragraph(f'<b><font color="#2d61d6">Извитость:</font></b> {VALUE_MAPPING[params["vessels_vein_turtuosity"]]}',
                  normal_style)
    ])

    table_data.append([
        Paragraph(
            f'<b><font color="#2d61d6">Бифуркация:</font></b> {VALUE_MAPPING[params["vessels_vein_bifurcation"]]}',
            normal_style)
    ])

    table_data.append([
        Paragraph(f'<b><font color="#2d61d6">Калибр:</font></b> {VALUE_MAPPING[params["vessels_vein_caliber"]]}',
                  normal_style)
    ])

    table_data.append([
        Paragraph(f'<b><font color="#2d61d6">A/B индекс:</font></b> {params["vessels_ratio"]}',
                  normal_style)
    ])

    table_data.append([
        Paragraph(f'<b><font color="#2d61d6">Патология:</font></b> {params["vessels_pathology"]}', normal_style)
    ])

    render(elements, title, image_buffer, table_data)


def add_macula(elements, title, image_buffer, params):
    if not image_buffer:
        return

    table_data = []

    table_data.append([
        Paragraph(
            f'<b><font color="#2d61d6">Макулярный рефлекс:</font></b> {VALUE_MAPPING[params["macula_macular_reflex"]]}',
            normal_style)
    ])

    table_data.append([
        Paragraph(
            f'<b><font color="#2d61d6">Фовеальный рефлекс:</font></b> {VALUE_MAPPING[params["macula_foveal_reflex"]]}',
            normal_style)
    ])

    table_data.append([
        Paragraph(f'<b><font color="#2d61d6">Патология:</font></b> {params["macula_pathology"]}', normal_style)
    ])

    render(elements, title, image_buffer, table_data)


@app.post("/api/v1/pdf", response_class=Response)
async def generation(
        current_service: CurrentServiceData,
        in_dto: PDFInDTO
):
    """
    Generates PDF report with estimated parameters, images and active text.
    """
    logger.info(f"Processing service={current_service.id}")

    # Обработка и комбинирование изображений
    def process_images(base_img_data, overlay_img_data):
        if not base_img_data or not overlay_img_data:
            return None
        try:
            base_img = Image.open(BytesIO(base64.b64decode(base_img_data))).convert("RGBA")
            overlay_img = Image.open(BytesIO(base64.b64decode(overlay_img_data))).convert("RGBA")
            combined = Image.alpha_composite(base_img, overlay_img)
            buffer = BytesIO()
            combined.save(buffer, format="PNG")
            buffer.seek(0)
            return buffer
        except Exception as e:
            logger.error(f"Image processing error: {str(e)}")
            return None

    images = {
        "od": process_images(in_dto.source_img, in_dto.od_img),
        "mac": process_images(in_dto.source_img, in_dto.mac_img),
        "av": process_images(in_dto.source_img, in_dto.av_img)
    }

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=18,
        title=f"Отчет №{in_dto.report_id}"
    )

    elements = []

    # Добавить шапку, что это отчет системы EYAS
    # Добавить шапку, что это отчет системы EYAS

    # Предумсотреть поле НОМЕР МЕДИЦИНСКОЙ / Амбулаторной КАРТЫ

    # Header
    elements.append(Paragraph(f"Отчет №{in_dto.report_id}", title_style))
    elements.append(Spacer(1, 6))
    # elements.append(Paragraph(f"<b>Дата генерации:</b> {current_service.created_at}", normal_style))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("Пациент: __________________________________________________", normal_style))

    add_OD(elements, "Диск зрительного нерва", images['od'], params=in_dto.params)

    add_vessels(elements, "Сосуды", images['av'], params=in_dto.params)

    elements.append(PageBreak())

    add_macula(elements, "Макула", images['mac'], params=in_dto.params)

    # Final Report
    elements.append(Paragraph("Описание", h2_style))
    elements.append(Spacer(1, 6))
    final_text = in_dto.text
    elements.append(Paragraph(final_text, report_text_style))
    elements.append(Spacer(1, 45))

    elements.append(Paragraph("Врач: __________________________________________________", normal_style))


    # Переферия -- Паталогия
    # Дипгноз

    doc.build(elements)
    buffer.seek(0)

    return Response(
        content=buffer.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": f"filename=report_{in_dto.report_id}.pdf"}
    )
