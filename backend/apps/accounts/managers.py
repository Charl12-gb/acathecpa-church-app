from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    """Custom user manager keyed off email (or phone). Mirrors FastAPI semantics."""

    use_in_migrations = True

    def _create_user(self, email=None, password=None, *, phone=None, **extra_fields):
        if not email and not phone:
            raise ValueError("Either email or phone must be provided")
        if email:
            email = self.normalize_email(email)
        user = self.model(email=email, phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email=email, password=password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self._create_user(email=email, password=password, **extra_fields)

    def get_by_natural_key(self, username):
        # Allow logging in with email OR phone
        return self.get(models_q_email_or_phone(username))


# helper kept at module level to avoid circular imports
def models_q_email_or_phone(value: str):
    from django.db.models import Q
    return Q(email__iexact=value) | Q(phone=value)
