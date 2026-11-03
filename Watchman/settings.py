import os
import re
from warnings import warn
from pathlib import Path
from logging.config import dictConfig
from urllib.parse import urlsplit

from django.core.exceptions import ImproperlyConfigured



def _env_bool(name, default):
    value = os.getenv(name)
    if value is None or value == "":
        return default
    return value.strip().lower() in ("1", "true", "yes", "on")


def _env_list(name):
    """Space- or comma-separated list from the environment."""
    return [item for item in re.split(r"[\s,]+", os.getenv(name) or "") if item]


BASE_URL = os.getenv("BASE_URL") or "http://localhost:8000"
VT_APIKEY = os.getenv("VT_APIKEY") or warn("No VT API key provided")
ENABLE_WEB_SCREENSHOT = os.getenv("ENABLE_WEB_SCREENSHOT") or False
I_UNDERSTAND_THIS_IS_DANGEROUS = os.getenv("I_UNDERSTAND_THIS_IS_DANGEROUS") or False

# Celery settings
CELERY_BROKER_URL = "redis://localhost:6379/0"

# Off in production: run-web.sh turns it off unless the config sets DEBUG explicitly.
DEBUG = _env_bool("DEBUG", True)
DBNAME = os.getenv("DBNAME") or warn(
    "No Database Name set in environment variable DBNAME"
)
DBUSER = os.getenv("DBUSER") or warn(
    "No Database User set in environment variable DBUSER"
)
DBPASSWORD = os.getenv("DBPASSWORD") or warn(
    "No Database Password set in environment variable DBPASSWORD"
)
DBHOST = os.getenv("DBHOST") or warn(
    "No Database Host set in environment variable DBHOST"
)
ICANN_USERNAME = os.getenv("ICANN_USERNAME") or warn(
    "No ICANN Username set in environment variable ICANN_USERNAME"
)
ICANN_PASSWORD = os.getenv("ICANN_PASSWORD") or warn(
    "No ICANN Password set in environment variable ICANN_PASSWORD"
)
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID") or warn(
    "No AWS Access Key ID set in environment variable"
)
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY") or warn(
    "No AWS Secret Access Key set in environment variable"
)
AWS_REGION_NAME = os.getenv("REGION_NAME") or "us-east-1"

BATCH_SIZE = os.getenv("BATCH_SIZE") or 50000
MIN_ZONE_TIME = os.getenv("MIN_ZONE_TIME") or 14400  # seconds
ZONE_UPDATE_INTERVAL = os.getenv("ZONE_UPDATE_INTERVAL") or 600.0  # seconds
MIN_UPDATE_INTERVAL = os.getenv("MIN_UPDATE_INTERVAL") or 600.0
MATCH_UPDATE_INTERVAL = os.getenv("MATCH_UPDATE_INTERVAL") or 600.0
MAX_NEW_AGE = os.getenv("MAX_NEW_AGE") or 400  # days
MAX_TEMP_AGE = os.getenv("MAX_TEMP_AGE") or 31  # days
DOMAIN_BUCKET_NAME = os.getenv("DOMAIN_BUCKET_NAME") or "domainlists"
NEWDOMAIN_BUCKET_NAME = os.getenv("NEWDOMAIN_BUCKET_NAME") or "newdomainlists"
MIN_DOMAIN_LIST_LENGTH = os.getenv("MIN_DOMAIN_LIST_LENGTH") or 10


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_DIRS = [
    f"{BASE_DIR}/templates/",
]

TEMP_DIR = f"{BASE_DIR}/tmp"

# AUTH_USER_MODEL = 'Watchman.CustomUser'
AUTH_USER_MODEL = "accounts.CustomUser"

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# The built-in key is only for development. With DEBUG off, DJANGO_SECRET_KEY
# must be set (install-web.sh generates one into the config file).
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY") or ""
if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = "django-insecure-s9n)tio7xscb%r4s_1v^rptbj*bb@ycm18(_@=%#mla#u#tut2"
    else:
        raise ImproperlyConfigured(
            "DJANGO_SECRET_KEY must be set when DEBUG is off. Generate one with "
            "install-web.sh or python -c 'from django.core.management.utils import "
            "get_random_secret_key as k; print(k())'"
        )


# The hosts this site answers for: the defaults, ALLOWED_HOSTS from the
# environment, and the host in BASE_URL.
_base_url = urlsplit(BASE_URL)
ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "watchman-dev.insomniac.tech",
]
for _host in _env_list("ALLOWED_HOSTS") + [_base_url.hostname or ""]:
    if _host and _host not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(_host)

# Origins allowed to POST (sign-in, admin). BASE_URL is always trusted.
CSRF_TRUSTED_ORIGINS = _env_list("CSRF_TRUSTED_ORIGINS")
if _base_url.scheme and _base_url.netloc:
    _origin = f"{_base_url.scheme}://{_base_url.netloc}"
    if _origin not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(_origin)

# Behind a load balancer or reverse proxy that terminates TLS, trust its
# X-Forwarded-Proto header so Django knows the request was HTTPS.
if _env_bool("USE_X_FORWARDED_PROTO", False):
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

if not DEBUG and _base_url.scheme == "https":
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# Application definition
INSTALLED_APPS = [
    "Watchman",
    "accounts",
    "django_bootstrap5",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
]

ROOT_URLCONF = "Watchman.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": TEMPLATE_DIRS,
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "Watchman.wsgi.application"


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": DBNAME,
        "USER": DBUSER,
        "PASSWORD": DBPASSWORD,
        "HOST": DBHOST,
        "PORT": "5432",
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}
STATIC_HOST = os.environ.get("DJANGO_STATIC_HOST", "")
STATIC_URL = STATIC_HOST + "/static/"

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": "general.log",
            "formatter": "verbose",
        },
        "celery": {
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "celery.log",
            "formatter": "simple",
            "maxBytes": 1024 * 1024 * 100,  # 100 mb
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": os.getenv("DJANGO_LOG_LEVEL", "INFO"),
            # "level": "DEBUG",
        },
        "celery": {
            "handlers": ["console"],
            "level": os.getenv("DJANGO_LOG_LEVEL", "INFO"),
            # "level": "DEBUG",
        },
    },
    "formatters": {
        "verbose": {
            "format": "{asctime}, {levelname}, {name}, {module}, {message}",
            "style": "{",
        },
        "simple": {
            "format": "{asctime} {levelname} {message}",
            "style": "{",
        },
    },
}

dictConfig(LOGGING)
