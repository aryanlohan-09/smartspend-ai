# Authentication

SmartSpend AI uses Flask-Login for session management and bcrypt for password hashing. Authentication routes live in the `auth` blueprint.

## Routes

| Method | Path | Purpose |
| --- | --- | --- |
| GET | /auth/register | Render registration form |
| POST | /auth/register | Validate input, create user, sign in |
| GET | /auth/login | Render login form |
| POST | /auth/login | Validate credentials and create session |
| POST | /auth/logout | End the authenticated session |

## Security Notes

- Passwords are hashed with bcrypt before persistence.
- Login redirects are validated to prevent open redirects.
- Session cookies are HTTP-only and production config enables secure cookies.
- Duplicate email registration is rejected.
- Logout uses POST to avoid accidental sign-outs from crawled links.
- POST, PUT, PATCH, and DELETE requests require a CSRF token from the user session.
