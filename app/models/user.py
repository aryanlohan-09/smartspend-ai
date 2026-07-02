from flask_login import UserMixin

from app.extensions import db
from app.models.base import TimestampMixin


class User(UserMixin, TimestampMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    last_login_at = db.Column(db.DateTime(timezone=True), nullable=True)

    receipts = db.relationship(
        "Receipt",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email!r}>"
