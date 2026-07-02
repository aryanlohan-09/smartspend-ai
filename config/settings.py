import os
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def _get_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _raw_database_uri() -> str:
    return os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://smartspend_user:smartspend_password@localhost:3306/smartspend_ai",
    )


def _database_uri() -> str:
    uri = _raw_database_uri()
    if uri.startswith("mysql://"):
        uri = uri.replace("mysql://", "mysql+pymysql://", 1)
    return _strip_unsupported_mysql_query_params(uri)


def _strip_unsupported_mysql_query_params(uri: str) -> str:
    parts = urlsplit(uri)
    query = [
        (key, value)
        for key, value in parse_qsl(parts.query, keep_blank_values=True)
        if key.lower() not in {"ssl-mode", "sslmode"}
    ]
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))


def _database_connect_args() -> dict:
    raw_uri = _raw_database_uri().lower()
    ssl_requested = "ssl-mode=" in raw_uri or "sslmode=" in raw_uri or _get_bool("DATABASE_SSL", False)
    if ssl_requested:
        return {"ssl": {}}
    return {}


class BaseConfig:
    APP_NAME = "SmartSpend AI"
    SECRET_KEY = os.getenv("SECRET_KEY", "change-this-development-secret")
    SQLALCHEMY_DATABASE_URI = _database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 280,
        "connect_args": _database_connect_args(),
    }
    AUTO_CREATE_TABLES = _get_bool("AUTO_CREATE_TABLES", False)

    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", str(BASE_DIR / "app" / "static" / "uploads"))
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH_MB", "8")) * 1024 * 1024
    ALLOWED_RECEIPT_EXTENSIONS = {"jpg", "jpeg", "png", "pdf"}
    EASYOCR_MODEL_DIR = os.getenv("EASYOCR_MODEL_DIR", str(BASE_DIR / ".easyocr"))

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
    AUTO_CREATE_TABLES = False
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "TEST_DATABASE_URL",
        "sqlite:///:memory:",
    )
    SQLALCHEMY_ENGINE_OPTIONS = {}


def get_config():
    env = os.getenv("FLASK_ENV", "development").lower()
    if env == "production":
        return ProductionConfig
    if env == "testing":
        return TestingConfig
    return DevelopmentConfig
