from sqlalchemy import select

from app.extensions import db
from app.models import Expense, Receipt
from app.services.ai.gemini_client import GeminiReceiptClient
from app.services.ai.schema import normalize_receipt_payload


class ExpenseAIService:
    def __init__(self, client: GeminiReceiptClient | None = None):
        self.client = client or GeminiReceiptClient()

    def create_expense_from_ocr(self, receipt: Receipt) -> Expense:
        if receipt.ocr_result is None:
            raise ValueError("Receipt must have OCR text before AI parsing.")

        payload = self.client.parse_receipt_text(receipt.ocr_result.raw_text)
        parsed = normalize_receipt_payload(payload)
        duplicate = self._find_semantic_duplicate(receipt, parsed)

        expense = Expense(
            receipt_id=receipt.id,
            merchant_name=parsed.merchant_name,
            receipt_number=parsed.receipt_number,
            purchased_at=parsed.purchased_at,
            total_amount=parsed.total_amount,
            gst_amount=parsed.gst_amount,
            currency=parsed.currency,
            payment_method=parsed.payment_method,
            category=parsed.category,
            ai_confidence_score=parsed.confidence_score,
            structured_data=parsed.structured_data,
        )
        db.session.add(expense)

        if duplicate is not None and receipt.duplicate_of_id is None:
            receipt.duplicate_of_id = duplicate.receipt_id

        return expense

    def _find_semantic_duplicate(self, receipt: Receipt, parsed) -> Expense | None:
        if not parsed.receipt_number:
            return None
        return db.session.scalar(
            select(Expense)
            .join(Receipt)
            .where(Receipt.user_id == receipt.user_id)
            .where(Receipt.id != receipt.id)
            .where(Expense.merchant_name == parsed.merchant_name)
            .where(Expense.total_amount == parsed.total_amount)
            .where(Expense.receipt_number == parsed.receipt_number)
            .order_by(Expense.created_at.asc())
        )
