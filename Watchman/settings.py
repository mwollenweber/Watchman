import os
from warnings import warn
from pathlib import Path

# Celery settings
CELERY_BROKER_URL = 'redis://localhost:6379/0'

DBNAME = os.getenv('DBNAME') or warn("No Database Name set in environment variable DBNAME")
DBUSER = os.getenv('DBUSER') or warn("No Database User set in environment variable DBUSER")
DBPASSWORD = os.getenv('DBPASSWORD') or warn("No Database Password set in environment variable DBPASSWORD")
DBHOST = os.getenv('DBHOST') or warn("No Database Host set in environment variable DBHOST")
ICANN_USERNAME = os.getenv('ICANN_USERNAME') or warn("No ICANN Username set in environment variable ICANN_USERNAME")
ICANN_PASSWORD = os.getenv('ICANN_PASSWORD') or warn("No ICANN Password set in environment variable ICANN_PASSWORD")

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_DIRS = [
    f"{BASE_DIR}/templates/",
]


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-s9n)tio7xscb%r4s_1v^rptbj*bb@ycm18(_@=%#mla#u#tut2"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    '.herokuapp.com',
    'localhost',
    '127.0.0.1',
]

# Application definition
INSTALLED_APPS = [
    "bootstrap5",
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
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
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
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': DBNAME,
        'USER': DBUSER,
        'PASSWORD': DBPASSWORD,
        'HOST': DBHOST,
        'PORT': '5432',
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
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATIC_HOST = os.environ.get("DJANGO_STATIC_HOST", "")
STATIC_URL = STATIC_HOST + "/static/"

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
