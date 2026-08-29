import io
import logging

logger = logging.getLogger(__name__)


class ReportLabPdfExporter:
    """Implementa ReportExporterPort usando reportlab.

    Antes, reportlab não estava em requirements.txt: sem a lib instalada, o
    fallback abaixo gravava texto puro num arquivo chamado ".pdf" sem avisar
    ninguém. Isso continua sendo o fallback aqui, mas agora reportlab está
    declarado como dependência e o problema fica logado se ainda assim faltar.
    """

    def to_pdf(self, text_content: str, company: str, timestamp: str) -> bytes:
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas
        except ImportError:
            logger.error("reportlab não está instalado - gerando bytes de texto puro em vez de um PDF real")
            return text_content.encode("utf-8")

        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter

        c.drawString(50, height - 50, f"=== {company} ===")
        c.drawString(50, height - 70, f"Gerado em: {timestamp}")

        y = height - 100
        for line in text_content.split("\n"):
            if y < 50:
                c.showPage()
                y = height - 50
            c.drawString(50, y, line[:90])
            y -= 15
        c.save()
        buffer.seek(0)
        return buffer.getvalue()
