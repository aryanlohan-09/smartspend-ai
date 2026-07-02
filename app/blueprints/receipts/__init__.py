from flask import Blueprint


receipts_bp = Blueprint("receipts", __name__, url_prefix="/receipts")

from app.blueprints.receipts import routes  # noqa: E402,F401
