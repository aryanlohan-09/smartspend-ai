# Render Deployment

SmartSpend AI is prepared for Render with a Docker deployment. Docker is used because OCR and PDF processing require system packages such as Poppler and OpenCV runtime libraries.

## Required Render Environment Variables

- `FLASK_ENV=production`
- `SECRET_KEY`
- `DATABASE_URL` using the SQLAlchemy MySQL format, for example `mysql+pymysql://user:password@host:3306/database`
- `GEMINI_API_KEY`
- `GEMINI_MODEL=gemini-1.5-flash`
- `UPLOAD_FOLDER=/app/app/static/uploads`
- `MAX_CONTENT_LENGTH_MB=8`

## Deployment Files

- `Dockerfile`: installs Python 3.12, app dependencies, Poppler, and OpenCV runtime libraries.
- `render.yaml`: Render Blueprint configuration.
- `wsgi.py`: production WSGI entry point.
- `Procfile`: non-Docker fallback command.

## Database Initialization

After the first deploy, open a Render shell and run:

```bash
flask --app wsgi:app init-db
```

For local MySQL setup, `scripts/create_mysql_database.sql` contains a starter database and user script. Change the password before using it outside local development.

## Health Check

Render can use `/health` as the health check path.

## Upload Storage Note

This project stores uploaded receipts on the service filesystem. For a long-running production system, move uploads to object storage such as S3-compatible storage. For a portfolio demo, local container storage is acceptable when uploads are treated as temporary demo data.
