from flask import render_template
from flask_login import current_user, login_required

from app.blueprints.insights import insights_bp
from app.services.insights import AIInsightService


@insights_bp.get("")
@login_required
def index():
    insight = AIInsightService().get_or_generate_monthly_insight(current_user.id)
    return render_template("insights/index.html", insight=insight)
