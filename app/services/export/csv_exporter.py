import csv
from io import StringIO

from sqlalchemy import select

from app.extensions import db
from app.models import Expense, Receipt


class CSVExportService:
    def export_user_expenses(self, user_id: int) -> str:
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "Merchant", "Date", "Total", "GST", "Currency", "Payment Method",
            "Category", "Receipt Number", "Filename",
        ])
        rows = db.session.execute(
            select(Expense, Receipt)
            .join(Receipt)
            .where(Receipt.user_id == user_id)
            .order_by(Expense.purchased_at.desc(), Receipt.created_at.desc())
        ).all()
        for expense, receipt in rows:
            writer.writerow([
                expense.merchant_name,
                expense.purchased_at.isoformat() if expense.purchased_at else "",
                expense.total_amount,
                expense.gst_amount or "",
                expense.currency,
                expense.payment_method.value,
                expense.category.value,
                expense.receipt_number or "",
                receipt.original_filename,
            ])
        return output.getvalue()
