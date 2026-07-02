from flask import current_app, redirect, url_for
from flask_login import current_user

from app.blueprints.core import core_bp


@core_bp.get("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))
    return redirect(url_for("auth.login"))


@core_bp.get("/health")
def health():
    return {
        "application": current_app.config["APP_NAME"],
        "status": "ok",
    }
