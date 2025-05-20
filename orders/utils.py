from io import BytesIO
from django.template.loader import get_template
from xhtml2pdf import pisa
import logging

logger = logging.getLogger(__name__)


def generate_invoice_pdf(order):
    try:
        template_path = 'orders/invoice_template.html'
        context = {'order': order}

        template = get_template(template_path)
        html = template.render(context)

        result = BytesIO()

        # PDF जनरेशन के विकल्प
        pdf = pisa.pisaDocument(
            BytesIO(html.encode("UTF-8")),
            result,
            encoding='UTF-8',
            link_callback=None
        )

        if pdf.err:
            logger.error(f"PDF generation error: {pdf.err}")
            return None

        pdf_data = result.getvalue()
        logger.info(f"PDF generated successfully, size: {len(pdf_data)} bytes")
        return pdf_data

    except Exception as e:
        logger.error(f"Error in generate_invoice_pdf: {str(e)}", exc_info=True)
        return None