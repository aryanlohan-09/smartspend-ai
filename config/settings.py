import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def _get_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _database_uri() -> str:
    return os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://smartspend_user:smartspend_password@localhost:3306/smartspend_ai",
    )


class BaseConfig:
    APP_NAME = "SmartSpend AI"
    SECRET_KEY = os.getenv("SECRET_KEY", "change-this-development-secret")
    SQLALCHEMY_DATABASE_URI = _database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 280,
    }

    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", str(BASE_DIR / "app" / "static" / "uploads"))
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH_MB", "8")) * 1024 * 1024
    ALLOWED_RECEIPT_EXTENSIONS = {"jpg", "jpeg", "png", "pdf"}

    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    REMEMBER_COOKIE_HTTPONLY = True

    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    SESSION_COOKIE_SECURE = False
    REMEMBER_COOKIE_SECURE = False


class ProductionConfig(BaseConfig):
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True


class TestingConfig(BaseConfig):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "TEST_DATABASE_URL",
        "sqlite:///:memory:",
    )


def get_config():
    env = os.getenv("FLASK_ENV", "development").lower()
    if env == "production":
        return ProductionConfig
    if env == "testing":
        return TestingConfig
    return DevelopmentConfig
