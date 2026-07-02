# Flask Architecture

SmartSpend AI uses the Flask application factory pattern. The app is created by `create_app` in `app/__init__.py`, which loads configuration, initializes extensions, registers blueprints, attaches error handlers, and applies security headers.

## Key Files

- `run.py`: local development entry point.
- `wsgi.py`: production WSGI entry point for Render and Gunicorn.
- `config/settings.py`: environment-driven configuration classes.
- `app/extensions.py`: shared SQLAlchemy, Flask-Login, and password hashing helpers.
- `app/blueprints/core`: lightweight root and health routes.
- `app/utils/errors.py`: centralized HTTP and unexpected error handling.
- `app/utils/http.py`: security response headers.
- `app/utils/logging.py`: production rotating-file logging.

## Environment

Copy `.env.example` to `.env` for local development and update the MySQL and Gemini values. Production values should be configured as Render environment variables.
