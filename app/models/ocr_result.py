from app.extensions import db
from app.models.base import TimestampMixin


class OCRResult(TimestampMixin, db.Model):
    __tablename__ = "ocr_results"

    id = db.Column(db.Integer, primary_key=True)
    receipt_id = db.Column(
        db.Integer,
        db.ForeignKey("receipts.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    raw_text = db.Column(db.Text, nullable=False)
    confidence_score = db.Column(db.Numeric(5, 4), nullable=True)
    engine = db.Column(db.String(80), nullable=False, default="EasyOCR")
    language_codes = db.Column(db.String(120), nullable=False, default="en")

    receipt = db.relationship("Receipt", back_populates="ocr_result")

    def __repr__(self) -> str:
        return f"<OCRResult id={self.id} receipt_id={self.receipt_id}>"
