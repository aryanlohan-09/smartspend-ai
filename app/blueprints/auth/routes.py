from datetime import datetime, timezone

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy import select

from app.blueprints.auth import auth_bp
from app.extensions import db, hash_password, verify_password
from app.forms import validate_login_form, validate_register_form
from app.models import User
from app.utils.security import is_safe_redirect_url


@auth_bp.get("/register")
def register():
    if current_user.is_authenticated:
        return redirect(url_for("receipts.upload"))
    return render_template("auth/register.html", form={}, errors={})


@auth_bp.post("/register")
def register_post():
    if current_user.is_authenticated:
        return redirect(url_for("receipts.upload"))

    result = validate_register_form(request.form)
    if not result.is_valid:
        return render_template(
            "auth/register.html",
            form=result.cleaned_data,
            errors=result.errors,
        ), 400

    email_exists = db.session.scalar(
        select(User.id).where(User.email == result.cleaned_data["email"])
    )
    if email_exists:
        errors = {"email": "An account with this email already exists."}
        return render_template(
            "auth/register.html",
            form=result.cleaned_data,
            errors=errors,
        ), 409

    user = User(
        name=result.cleaned_data["name"],
        email=result.cleaned_data["email"],
        password_hash=hash_password(result.cleaned_data["password"]),
    )
    db.session.add(user)
    db.session.commit()

    login_user(user)
    flash("Account created successfully.", "success")
    return redirect(url_for("receipts.upload"))


@auth_bp.get("/login")
def login():
    if current_user.is_authenticated:
        return redirect(url_for("receipts.upload"))
    return render_template("auth/login.html", form={}, errors={})


@auth_bp.post("/login")
def login_post():
    if current_user.is_authenticated:
        return redirect(url_for("receipts.upload"))

    result = validate_login_form(request.form)
    if not result.is_valid:
        return render_template(
            "auth/login.html",
            form=result.cleaned_data,
            errors=result.errors,
        ), 400

    user = db.session.scalar(
        select(User).where(User.email == result.cleaned_data["email"])
    )
    if user is None or not verify_password(result.cleaned_data["password"], user.password_hash):
        errors = {"form": "Invalid email or password."}
        return render_template(
            "auth/login.html",
            form=result.cleaned_data,
            errors=errors,
        ), 401

    user.last_login_at = datetime.now(timezone.utc)
    db.session.commit()
    login_user(user, remember=request.form.get("remember") == "on")

    next_url = request.args.get("next")
    if is_safe_redirect_url(next_url):
        return redirect(next_url)
    return redirect(url_for("receipts.upload"))


@auth_bp.post("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been signed out.", "info")
    return redirect(url_for("auth.login"))
