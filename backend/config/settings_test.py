"""
Test settings: same as production but with an in-memory SQLite database
and fast password hashing. Loaded via DJANGO_SETTINGS_MODULE in pytest.ini.
"""
from .settings import *  # noqa: F401,F403

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}


# Skip running migrations: create tables directly from current models
class _DisableMigrations:
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None


MIGRATION_MODULES = _DisableMigrations()

# Speed up password hashing during tests
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# Email backend captured in memory
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# Avoid relying on real Jitsi credentials
JITSI_APP_ID = ""
JITSI_DOMAIN = "8x8.test"
JITSI_JWT = ""
