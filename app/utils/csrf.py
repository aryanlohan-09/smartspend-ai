import secrets

from flask import Flask, abort, request, session


_CSRF_SESSION_KEY = "_csrf_token"


def generate_csrf_token() -> str:
    token = session.get(_CSRF_SESSION_KEY)
    if token is None:
        token = secrets.token_urlsafe(32)
        session[_CSRF_SESSION_KEY] = token
    return token


def register_csrf_protection(app: Flask) -> None:
    @app.context_processor
    def inject_csrf_token():
        return {"csrf_token": generate_csrf_token}

    @app.before_request
    def validate_csrf_token():
        if request.method not in {"POST", "PUT", "PATCH", "DELETE"}:
            return None
        expected = session.get(_CSRF_SESSION_KEY)
        supplied = request.form.get("csrf_token") or request.headers.get("X-CSRF-Token")
        if not expected or not supplied or not secrets.compare_digest(expected, supplied):
            abort(400, description="Invalid or missing CSRF token.")
        return None
