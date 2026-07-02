from io import BytesIO

from sqlalchemy import select

from app.extensions import db
from app.models import Expense, Receipt


class PDFExportService:
    def export_user_expenses(self, user_id: int) -> bytes:
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
        except ImportError as exc:
            raise RuntimeError("PDF export requires reportlab to be installed.") from exc

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, title="SmartSpend AI Expense Export")
        styles = getSampleStyleSheet()
        rows = [["Merchant", "Date", "Total", "Category"]]
        expenses = db.session.execute(
            select(Expense)
            .join(Receipt)
            .where(Receipt.user_id == user_id)
            .order_by(Expense.purchased_at.desc(), Receipt.created_at.desc())
        ).scalars().all()
        for expense in expenses:
            rows.append([
                expense.merchant_name,
                expense.purchased_at.strftime("%Y-%m-%d") if expense.purchased_at else "",
                f"{expense.currency} {expense.total_amount}",
                expense.category.value,
            ])

        table = Table(rows, repeatRows=1)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f6f8fa")),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#d0d7de")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        doc.build([Paragraph("SmartSpend AI Expense Export", styles["Title"]), Spacer(1, 12), table])
        return buffer.getvalue()
