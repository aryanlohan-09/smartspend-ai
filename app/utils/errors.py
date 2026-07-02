from flask import Flask, jsonify, render_template, request
from werkzeug.exceptions import HTTPException


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(HTTPException)
    def handle_http_error(error: HTTPException):
        if _expects_json():
            return jsonify(error=error.name, message=error.description), error.code
        return render_template("errors/error.html", error=error), error.code

    @app.errorhandler(Exception)
    def handle_unexpected_error(error: Exception):
        app.logger.exception("Unhandled application error", exc_info=error)
        if _expects_json():
            return jsonify(error="Internal Server Error", message="An unexpected error occurred."), 500
        return render_template("errors/500.html"), 500


def _expects_json() -> bool:
    return request.accept_mimetypes.best == "application/json"
