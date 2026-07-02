from app.extensions import db
from app.models.base import TimestampMixin
from app.models.enums import ReceiptStatus


class Receipt(TimestampMixin, db.Model):
    __tablename__ = "receipts"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    original_filename = db.Column(db.String(255), nullable=False)
    stored_filename = db.Column(db.String(255), nullable=False, unique=True)
    file_path = db.Column(db.String(500), nullable=False)
    file_mime_type = db.Column(db.String(100), nullable=False)
    file_size_bytes = db.Column(db.Integer, nullable=False)
    file_hash = db.Column(db.String(64), nullable=False, index=True)
    status = db.Column(
        db.Enum(ReceiptStatus),
        nullable=False,
        default=ReceiptStatus.UPLOADED,
    )
    failure_reason = db.Column(db.String(500), nullable=True)
    duplicate_of_id = db.Column(
        db.Integer,
        db.ForeignKey("receipts.id", ondelete="SET NULL"),
        nullable=True,
    )

    user = db.relationship("User", back_populates="receipts")
    duplicate_of = db.relationship("Receipt", remote_side=[id])
    ocr_result = db.relationship(
        "OCRResult",
        back_populates="receipt",
        cascade="all, delete-orphan",
        uselist=False,
    )
    expense = db.relationship(
        "Expense",
        back_populates="receipt",
        cascade="all, delete-orphan",
        uselist=False,
    )

    def __repr__(self) -> str:
        return f"<Receipt id={self.id} user_id={self.user_id} status={self.status.value}>"
