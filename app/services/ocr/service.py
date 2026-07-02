from pathlib import Path

from sqlalchemy import select

from app.extensions import db
from app.models import OCRResult, Receipt, ReceiptStatus
from app.services.ai import ExpenseAIService
from app.services.ocr.engine import EasyOCRReceiptReader
from app.services.storage import store_receipt_file


class ReceiptOCRService:
    def __init__(
        self,
        reader: EasyOCRReceiptReader | None = None,
        expense_service: ExpenseAIService | None = None,
    ):
        self.reader = reader or EasyOCRReceiptReader()
        self.expense_service = expense_service or ExpenseAIService()

    def create_receipt_from_upload(self, file, user_id: int) -> Receipt:
        stored_file = store_receipt_file(file)
        existing = self._find_existing_by_hash(user_id, stored_file.sha256_hash)
        if existing is not None:
            Path(stored_file.file_path).unlink(missing_ok=True)
            return existing

        receipt = Receipt(
            user_id=user_id,
            original_filename=stored_file.original_filename,
            stored_filename=stored_file.stored_filename,
            file_path=stored_file.file_path,
            file_mime_type=stored_file.mime_type,
            file_size_bytes=stored_file.size_bytes,
            file_hash=stored_file.sha256_hash,
            status=ReceiptStatus.PROCESSING,
        )
        db.session.add(receipt)
        db.session.commit()

        try:
            extraction = self.reader.extract_text(stored_file.file_path, stored_file.extension)
            ocr_result = OCRResult(
                receipt_id=receipt.id,
                raw_text=extraction.text or "No readable text was detected.",
                confidence_score=extraction.confidence_score,
                language_codes=extraction.language_codes,
            )
            receipt.ocr_result = ocr_result
            db.session.add(ocr_result)
            db.session.flush()

            self.expense_service.create_expense_from_ocr(receipt)
            receipt.status = ReceiptStatus.PROCESSED
            db.session.commit()
        except Exception as exc:
            db.session.rollback()
            receipt = db.session.get(Receipt, receipt.id)
            receipt.status = ReceiptStatus.FAILED
            receipt.failure_reason = str(exc)[:500]
            db.session.commit()

        return receipt

    def _find_existing_by_hash(self, user_id: int, file_hash: str) -> Receipt | None:
        return db.session.scalar(
            select(Receipt)
            .where(Receipt.user_id == user_id)
            .where(Receipt.file_hash == file_hash)
            .order_by(Receipt.created_at.asc())
        )
