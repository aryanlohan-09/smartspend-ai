from flask import Response
from flask_login import current_user, login_required

from app.blueprints.exports import exports_bp
from app.services.export import CSVExportService, PDFExportService


@exports_bp.get("/csv")
@login_required
def csv_export():
    csv_data = CSVExportService().export_user_expenses(current_user.id)
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=smartspend-expenses.csv"},
    )


@exports_bp.get("/pdf")
@login_required
def pdf_export():
    pdf_data = PDFExportService().export_user_expenses(current_user.id)
    return Response(
        pdf_data,
        mimetype="application/pdf",
        headers={"Content-Disposition": "attachment; filename=smartspend-expenses.pdf"},
    )
