from flask import abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import select

from app.blueprints.receipts import receipts_bp
from app.extensions import db
from app.models import ExpenseCategory, Receipt, ReceiptStatus
from app.services.history import ReceiptHistoryService
from app.services.ocr import ReceiptOCRService


@receipts_bp.get("")
@login_required
def history():
    receipts, pagination = ReceiptHistoryService().search(current_user.id, request.args)
    return render_template(
        "receipts/history.html",
        receipts=receipts,
        pagination=pagination,
        categories=[category.value for category in ExpenseCategory],
    )


@receipts_bp.get("/upload")
@login_required
def upload():
    return render_template("receipts/upload.html")


@receipts_bp.post("/upload")
@login_required
def upload_post():
    file = request.files.get("receipt")
    service = ReceiptOCRService()

    try:
        receipt = service.create_receipt_from_upload(file, current_user.id)
    except ValueError as exc:
        flash(str(exc), "warning")
        return redirect(url_for("receipts.upload"))

    if receipt.status == ReceiptStatus.FAILED:
        flash("Receipt uploaded, but processing failed. Details are shown below.", "warning")
    elif receipt.status == ReceiptStatus.DUPLICATE:
        flash("Receipt uploaded and matched to an earlier receipt.", "info")
    else:
        flash("Receipt uploaded, scanned, and categorized.", "success")

    return redirect(url_for("receipts.detail", receipt_id=receipt.id))


@receipts_bp.get("/<int:receipt_id>")
@login_required
def detail(receipt_id: int):
    receipt = _user_receipt_or_404(receipt_id)
    return render_template("receipts/detail.html", receipt=receipt)


def _user_receipt_or_404(receipt_id: int) -> Receipt:
    receipt = db.session.scalar(
        select(Receipt)
        .where(Receipt.id == receipt_id)
        .where(Receipt.user_id == current_user.id)
    )
    if receipt is None:
        abort(404)
    return receipt
