import click
from flask import Flask

from app.extensions import db


def register_cli_commands(app: Flask) -> None:
    @app.cli.command("init-db")
    def init_db():
        from app import models  # noqa: F401

        db.create_all()
        click.echo("Database tables created.")

    @app.cli.command("check-config")
    def check_config():
        required = ["SECRET_KEY", "SQLALCHEMY_DATABASE_URI", "GEMINI_API_KEY"]
        missing = [key for key in required if not app.config.get(key)]
        if missing:
            raise click.ClickException(f"Missing required settings: {', '.join(missing)}")
        click.echo("Configuration looks ready.")
