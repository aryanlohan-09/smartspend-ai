import re
from dataclasses import dataclass, field


_EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@dataclass
class ValidationResult:
    cleaned_data: dict = field(default_factory=dict)
    errors: dict = field(default_factory=dict)

    @property
    def is_valid(self) -> bool:
        return not self.errors


def validate_register_form(form_data) -> ValidationResult:
    name = form_data.get("name", "").strip()
    email = form_data.get("email", "").strip().lower()
    password = form_data.get("password", "")
    confirm_password = form_data.get("confirm_password", "")
    errors = {}

    if len(name) < 2:
        errors["name"] = "Enter your full name."
    if not _EMAIL_PATTERN.match(email):
        errors["email"] = "Enter a valid email address."
    if len(password) < 8:
        errors["password"] = "Password must be at least 8 characters."
    elif not _has_letter_and_number(password):
        errors["password"] = "Password must include at least one letter and one number."
    if password != confirm_password:
        errors["confirm_password"] = "Passwords do not match."

    return ValidationResult(
        cleaned_data={"name": name, "email": email, "password": password},
        errors=errors,
    )


def validate_login_form(form_data) -> ValidationResult:
    email = form_data.get("email", "").strip().lower()
    password = form_data.get("password", "")
    errors = {}

    if not _EMAIL_PATTERN.match(email):
        errors["email"] = "Enter a valid email address."
    if not password:
        errors["password"] = "Enter your password."

    return ValidationResult(
        cleaned_data={"email": email, "password": password},
        errors=errors,
    )


def _has_letter_and_number(value: str) -> bool:
    return any(char.isalpha() for char in value) and any(char.isdigit() for char in value)
