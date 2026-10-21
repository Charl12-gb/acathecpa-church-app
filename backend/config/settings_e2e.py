"""
Settings for the Playwright end-to-end tests: a throw-away SQLite database
(rebuilt by tests/e2e_seed.py) instead of the XAMPP MySQL one.
"""
from .settings import *  # noqa: F401,F403
from .settings import BASE_DIR

E2E_DIR = BASE_DIR / ".e2e"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": E2E_DIR / "db.sqlite3",
    }
}

# Files uploaded by the tests stay out of backend/media.
MEDIA_ROOT = E2E_DIR / "media"

DEBUG = True
CORS_ALLOWED_ORIGINS = ["http://localhost:5174", "http://127.0.0.1:5174"]
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
PAYMENT_PROVIDER = "simulation"
JITSI_APP_ID = ""
