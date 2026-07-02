from pathlib import Path

from flask import Flask
from sqlalchemy.exc import OperationalError

from app.extensions import db, login_manager
from app.utils.csrf import register_csrf_protection
from app.utils.http import register_security_headers
from app.utils.logging import configure_logging
from config import get_config


def create_app(config_object=None) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_object or get_config())

    configure_logging(app)
    _ensure_runtime_directories(app)
    _init_extensions(app)
    _create_tables_if_enabled(app)
    register_csrf_protection(app)
    _register_blueprints(app)
    _register_error_handlers(app)
    _register_cli_commands(app)
    register_security_headers(app)

    app.logger.info("SmartSpend AI application initialized")
    return app


def _ensure_runtime_directories(app: Flask) -> None:
    upload_folder = Path(app.config["UPLOAD_FOLDER"])
    upload_folder.mkdir(parents=True, exist_ok=True)


def _init_extensions(app: Flask) -> None:
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "warning"

    from app.models import User

    @login_manager.user_loader
    def load_user(user_id: str):
        if not user_id.isdigit():
            return None
        return db.session.get(User, int(user_id))


def _create_tables_if_enabled(app: Flask) -> None:
    if not app.config.get("AUTO_CREATE_TABLES"):
        return
    with app.app_context():
        from app import models  # noqa: F401

        try:
            db.create_all()
            app.logger.info("Database tables verified via AUTO_CREATE_TABLES")
        except OperationalError as exc:
            if _is_mysql_table_exists_error(exc):
                app.logger.info("Database tables already exist; continuing startup")
                return
            raise


def _is_mysql_table_exists_error(exc: OperationalError) -> bool:
    original = getattr(exc, "orig", None)
    error_code = original.args[0] if original and getattr(original, "args", None) else None
    return error_code == 1050


def _register_blueprints(app: Flask) -> None:
    from app.blueprints.auth import auth_bp
    from app.blueprints.core import core_bp
    from app.blueprints.dashboard import dashboard_bp
    from app.blueprints.exports import exports_bp
    from app.blueprints.insights import insights_bp
    from app.blueprints.receipts import receipts_bp

    app.register_blueprint(core_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(receipts_bp)
    app.register_blueprint(insights_bp)
    app.register_blueprint(exports_bp)


def _register_error_handlers(app: Flask) -> None:
    from app.utils.errors import register_error_handlers

    register_error_handlers(app)


def _register_cli_commands(app: Flask) -> None:
    from app.cli import register_cli_commands

    register_cli_commands(app)
