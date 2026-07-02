from app.extensions import db
from app.models.base import TimestampMixin
from app.models.enums import ExpenseCategory, PaymentMethod


class Expense(TimestampMixin, db.Model):
    __tablename__ = "expenses"

    id = db.Column(db.Integer, primary_key=True)
    receipt_id = db.Column(
        db.Integer,
        db.ForeignKey("receipts.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    merchant_name = db.Column(db.String(255), nullable=False, index=True)
    receipt_number = db.Column(db.String(120), nullable=True, index=True)
    purchased_at = db.Column(db.DateTime(timezone=True), nullable=True, index=True)
    total_amount = db.Column(db.Numeric(12, 2), nullable=False, index=True)
    gst_amount = db.Column(db.Numeric(12, 2), nullable=True)
    currency = db.Column(db.String(3), nullable=False, default="INR")
    payment_method = db.Column(
        db.Enum(PaymentMethod),
        nullable=False,
        default=PaymentMethod.UNKNOWN,
    )
    category = db.Column(
        db.Enum(ExpenseCategory),
        nullable=False,
        default=ExpenseCategory.OTHER,
        index=True,
    )
    ai_confidence_score = db.Column(db.Numeric(5, 4), nullable=True)
    structured_data = db.Column(db.JSON, nullable=False)

    receipt = db.relationship("Receipt", back_populates="expense")

    __table_args__ = (
        db.Index(
            "ix_expenses_duplicate_lookup",
            "merchant_name",
            "total_amount",
            "receipt_number",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<Expense id={self.id} merchant={self.merchant_name!r} "
            f"amount={self.total_amount}>"
        )
