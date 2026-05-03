"""
Custom MySQL/MariaDB backend that skips Django's database version check.

XAMPP ships with MariaDB 10.4.x but Django 5.x requires MariaDB >= 10.5.
The check is conservative (most features used here work fine on 10.4),
so we override `check_database_version_supported` to a no-op.

Usage in settings.py::

    DATABASES = {
        "default": {
            "ENGINE": "config.db_backends.mysql_no_version_check",
            ...
        }
    }
"""
from django.db.backends.mysql import base, features


class DatabaseFeatures(features.DatabaseFeatures):
    # MariaDB 10.4 does not support `INSERT ... RETURNING` (added in 10.5).
    can_return_columns_from_insert = False
    can_return_rows_from_bulk_insert = False


class DatabaseWrapper(base.DatabaseWrapper):
    features_class = DatabaseFeatures

    def check_database_version_supported(self):  # noqa: D401
        # XAMPP MariaDB 10.4 is OK for our usage — bypass Django's check.
        return
