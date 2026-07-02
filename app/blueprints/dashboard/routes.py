from flask import render_template
from flask_login import current_user, login_required

from app.blueprints.dashboard import dashboard_bp
from app.services.dashboard import DashboardService


@dashboard_bp.get("")
@login_required
def index():
    metrics = DashboardService().get_metrics(current_user.id)
    return render_template("dashboard/index.html", metrics=metrics)
