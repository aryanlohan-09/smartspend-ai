from flask import Blueprint


insights_bp = Blueprint("insights", __name__, url_prefix="/insights")

from app.blueprints.insights import routes  # noqa: E402,F401
