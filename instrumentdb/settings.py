# -*- encoding: utf-8 -*-

"""
Django settings for instrumentdb project.

Generated by 'django-admin startproject' using Django 3.0.3.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

from pathlib import Path
import os

from django.conf import settings
from envparse import Env

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

env = Env(
    DEBUG=bool,
    SECRET_KEY=str,
    ALLOWED_HOSTS=dict(cast=list, subcast=str),
    STORAGE_PATH=dict(cast=str, default="var"),
    DATABASE_URL=dict(cast=str, default=str(Path("var") / "instrumentdb.sqlite3")),
)
env.read_envfile()

# Be sure to check
# https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

SECRET_KEY = env("SECRET_KEY")
DEBUG = env("DEBUG")
ALLOWED_HOSTS = env("ALLOWED_HOSTS")
MEDIA_ROOT = Path(env("STORAGE_PATH"))

if env.bool("LOGGING"):
    log_file_path = env("LOG_FILE_PATH", default="")
    formatter = env("LOG_FORMATTER", default="brief")

    if log_file_path != "":
        log_file_path = Path(log_file_path)
        # Ensure that the directory where the log file is to be created exists
        log_file_path.parent.mkdir(parents=True, exist_ok=True)

        log_handler = {
            "file": {
                "level": env("LOG_LEVEL"),
                "class": "logging.FileHandler",
                "filename": log_file_path,
                "formatter": formatter,
            },
        }

    else:
        log_handler = {
            "console": {
                "level": env("LOG_LEVEL"),
                "class": "logging.StreamHandler",
                "formatter": formatter,
            },
        }

    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": log_handler,
        "formatters": {
            "brief": {
                "format": "{levelname} {asctime} {message}",
                "style": "{",
            },
            "verbose": {
                "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
                "style": "{",
            },
        },
        "loggers": {
            "django": {
                "handlers": list(log_handler.keys()),
                "level": env("LOG_LEVEL"),
                "propagate": True,
            },
        },
    }


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "mptt",
    "browse",
    "rest_framework.authtoken",
    "sslserver",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.gzip.GZipMiddleware",
]

ROOT_URLCONF = "instrumentdb.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

WSGI_APPLICATION = "instrumentdb.wsgi.application"

# REST API

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_AUTHENTICATION_CLASSES": (
        # "rest_framework.authentication.TokenAuthentication",
        "instrumentdb.authentication.ExpiringTokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 25,
}

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases


def django_sqlite(file_name):
    return {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": file_name,
    }


DATABASES = {"default": env("DATABASE_URL", postprocessor=django_sqlite)}


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = "static/"
STATIC_ROOT = env("STATIC_PATH", default=os.path.join(BASE_DIR, "static"))
LOGIN_REDIRECT_URL = "/accounts/login/"
LOGOUT_REDIRECT_URL = "/"
ADMIN_MEDIA_PREFIX = "/static/admin/"

TOKEN_EXPIRED_AFTER_MINUTES = 15

SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 3600  # (seconds) #86400 #1day
