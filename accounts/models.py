import secrets
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone
from django.utils.crypto import constant_time_compare, salted_hmac


def normalize_email(email):
    """Lower-case and trim an address so lookups and uniqueness are case-insensitive."""
    return (email or "").strip().lower()


class CustomUserManager(BaseUserManager):
    """Users are identified by email. There are no usernames and no usable passwords."""

    use_in_migrations = True

    def _create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("An email address is required")
        user = self.model(email=normalize_email(email), **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("user_type", "admin")
        if not extra_fields["is_staff"] or not extra_fields["is_superuser"]:
            raise ValueError("A superuser must have is_staff=True and is_superuser=True")
        return self._create_user(email, password, **extra_fields)

    def get_by_natural_key(self, email):
        return self.get(**{f"{self.model.USERNAME_FIELD}__iexact": normalize_email(email)})


class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ("client", "client"),
        ("clientAdmin", "clientAdmin"),
        ("admin", "admin"),
    )

    # No usernames: the email address identifies the account. Login is by
    # one-time code sent to that address (see LoginCode), so the inherited
    # password field is only ever set to an unusable value.
    username = None
    email = models.EmailField("email address", unique=True)
    user_type = models.CharField(
        max_length=20, choices=USER_TYPE_CHOICES, default="client"
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def is_admin(self):
        return self.user_type == "admin"

    def __str__(self):
        return self.email


class LoginCodeError(Exception):
    """A code could not be issued or verified. The message is safe to show the user."""


class LoginCode(models.Model):
    """A one-time numeric code emailed to an address to sign in.

    Only an HMAC of the code is stored. A code is valid once, until it
    expires, and only for a limited number of guesses.
    """

    CODE_LENGTH = 6

    email = models.EmailField(db_index=True)
    code_hash = models.CharField(max_length=64)
    created = models.DateTimeField(default=timezone.now, db_index=True)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)
    attempts = models.PositiveSmallIntegerField(default=0)
    requested_ip = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return f"{self.email} ({self.created:%Y-%m-%d %H:%M})"

    # --- helpers -----------------------------------------------------------

    @staticmethod
    def hash_code(email, code):
        return salted_hmac(
            "accounts.LoginCode", f"{normalize_email(email)}:{code}", algorithm="sha256"
        ).hexdigest()

    @classmethod
    def generate_code(cls):
        return f"{secrets.randbelow(10 ** cls.CODE_LENGTH):0{cls.CODE_LENGTH}d}"

    @property
    def is_expired(self):
        return self.expires_at <= timezone.now()

    @property
    def is_usable(self):
        return (
            self.used_at is None
            and not self.is_expired
            and self.attempts < settings.LOGIN_CODE_MAX_ATTEMPTS
        )

    def invalidate(self):
        self.expires_at = timezone.now()
        self.save(update_fields=["expires_at"])

    # --- issue / verify ------------------------------------------------------

    @classmethod
    def issue(cls, email, ip=None):
        """Create a fresh code for `email`, retiring any outstanding one.

        Returns (login_code, plain_code). Raises LoginCodeError when the
        address has asked for codes too quickly or too often.
        """
        email = normalize_email(email)
        now = timezone.now()

        recent = cls.objects.filter(email=email, created__gt=now - timedelta(hours=1))
        if recent.count() >= settings.LOGIN_CODE_MAX_PER_HOUR:
            raise LoginCodeError(
                "Too many codes have been requested for that address. "
                "Please try again in an hour."
            )
        latest = recent.first()
        if latest:
            wait = settings.LOGIN_CODE_RESEND_SECONDS - (now - latest.created).total_seconds()
            if wait > 0:
                raise LoginCodeError(
                    f"A code was just sent. Please wait {int(wait) + 1} seconds "
                    "before requesting another."
                )

        cls.objects.filter(email=email, used_at__isnull=True, expires_at__gt=now).update(
            expires_at=now
        )

        code = cls.generate_code()
        login_code = cls.objects.create(
            email=email,
            code_hash=cls.hash_code(email, code),
            created=now,
            expires_at=now + timedelta(minutes=settings.LOGIN_CODE_TTL_MINUTES),
            requested_ip=ip,
        )
        return login_code, code

    @classmethod
    def verify(cls, email, code):
        """Consume the current code for `email` if `code` matches.

        Returns True on success. Raises LoginCodeError with a message for
        the user otherwise. Every wrong guess counts against the code.
        """
        email = normalize_email(email)
        now = timezone.now()
        login_code = (
            cls.objects.filter(email=email, used_at__isnull=True, expires_at__gt=now)
            .order_by("-created")
            .first()
        )
        if login_code is None:
            raise LoginCodeError("That code has expired. Please request a new one.")

        login_code.attempts += 1
        login_code.save(update_fields=["attempts"])

        if login_code.attempts > settings.LOGIN_CODE_MAX_ATTEMPTS:
            login_code.invalidate()
            raise LoginCodeError("Too many incorrect attempts. Please request a new code.")

        if not constant_time_compare(login_code.code_hash, cls.hash_code(email, code)):
            remaining = settings.LOGIN_CODE_MAX_ATTEMPTS - login_code.attempts
            if remaining <= 0:
                login_code.invalidate()
                raise LoginCodeError(
                    "Too many incorrect attempts. Please request a new code."
                )
            raise LoginCodeError(
                f"That code is not correct. {remaining} "
                f"attempt{'s' if remaining != 1 else ''} left."
            )

        login_code.used_at = now
        login_code.save(update_fields=["used_at"])
        return True
