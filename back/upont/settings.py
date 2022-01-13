"""
Django settings for upont project.

Generated by 'django-admin startproject' using Django 3.2.6.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

import os
from pathlib import Path

import environ

# getting environmnent variables
env = environ.Env()
environ.Env.read_env()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env("DEBUG", default=False)

ALLOWED_HOSTS = [
    "upont.enpc.org",
    "upont-dev.enpc.org",
    "localhost",
    "127.0.0.1",
    "back",
]

if DEBUG:
    # SECURITY WARNING: keep the secret key used in production secret!
    SECRET_KEY = "django-insecure-2-e3q#*pqsgm+lhrgrkc=ex%!^8(3^*6@q^367*ma4j1$=54$f"
else:
    SECRET_KEY = env("SECRET_KEY", default=None)


# Application definition

INSTALLED_APPS = [
    "news.apps.NewsConfig",
    "pochtron.apps.PochtronConfig",
    "social.apps.SocialConfig",
    "trade.apps.TradeConfig",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "tellme",
    "django.contrib.postgres",
    "mod_wsgi.server",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "upont.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "upont/templates/upont")],
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

WSGI_APPLICATION = "upont.wsgi.application"


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": os.environ["DB_HOST"],
        "PORT": os.environ["DB_PORT"],
        "NAME": os.environ["DB_NAME"],
        "USER": os.environ["DB_USER"],
        "PASSWORD": os.environ["DB_PASSWORD"],
    }
}


# Login redirection

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "social:index_users"


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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

AUTHENTICATION_BACKENDS = [
    "upont.auth.EmailBackend",
    "django.contrib.auth.backends.ModelBackend",
]

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = "fr-fr"

TIME_ZONE = "Europe/Paris"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "../static/")
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "upont/static"),
]

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

FIXTURE_DIRS = ["/fixtures/"]

# Default media folder
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "../media/")

# Email backend
if DEBUG:
    DEFAULT_FROM_EMAIL = "test@mail.com"
    EMAIL_FILE_PATH = os.path.join(BASE_DIR, "../emails/")
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
    SENDGRID_SANDBOX_MODE_IN_DEBUG = True
else:
    DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="upont@enpc.org")
    EMAIL_BACKEND = "sendgrid_backend.SendgridBackend"
    SENDGRID_API_KEY = env("SENDGRID_API_KEY", default=None)
    ADMIN_EMAIL = env("ADMIN_EMAIL", default=None)
    SENDGRID_SANDBOX_MODE_IN_DEBUG = False
