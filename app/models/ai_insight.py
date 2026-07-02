from app.extensions import db
from app.models.base import TimestampMixin


class AIInsight(TimestampMixin, db.Model):
    __tablename__ = "ai_insights"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    month = db.Column(db.Date, nullable=False, index=True)
    summary = db.Column(db.Text, nullable=False)
    largest_category = db.Column(db.String(80), nullable=False)
    spending_habits = db.Column(db.Text, nullable=False)
    saving_suggestions = db.Column(db.Text, nullable=False)
    model_name = db.Column(db.String(120), nullable=False)

    user = db.relationship("User")

    __table_args__ = (
        db.UniqueConstraint("user_id", "month", name="uq_ai_insights_user_month"),
    )

    def __repr__(self) -> str:
        return f"<AIInsight id={self.id} user_id={self.user_id} month={self.month}>"
