import logging

import sentry_sdk
from django_secrets import SECRETS

from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

# from sentry_sdk.integrations.celery import CeleryIntegration

from .base import *  # noqa


# ENVIRON
# ------------------------------------------------------------------------------
# https://github.com/LeeHanYeong/django-aws-secrets-manager
AWS_SECRETS_MANAGER_SECRETS_SECTION = 'django-base:production'


# GENERAL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
SECRET_KEY = SECRETS["DJANGO_SECRET_KEY"]
# https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts
ALLOWED_HOSTS = SECRETS["ALLOWED_HOSTS"]


# DATABASES
# ------------------------------------------------------------------------------
DATABASES = dict()
DATABASES["default"] = dict()
DATABASES["default"]['ENGINE'] = SECRETS["DATABASE_ENGINE"]  # noqa
DATABASES["default"]['HOST'] = SECRETS["DATABASE_URL"]  # noqa
DATABASES["default"]["NAME"] = SECRETS["DATABASE_NAME"]  # noqa
DATABASES["default"]["USER"] = SECRETS["DATABASE_USER"]  # noqa
DATABASES["default"]["PASSWORD"] = SECRETS["DATABASE_PASSWORD"]  # noqa
DATABASES["default"]["PORT"] = SECRETS.get("DATABASE_PORT", default=5432)  # noqa
DATABASES["default"]["CONN_MAX_AGE"] = SECRETS.get("CONN_MAX_AGE", default=60)  # noqa


# ADMIN
# ------------------------------------------------------------------------------
# Django Admin URL.
ADMIN_URL = "admin/"
# https://docs.djangoproject.com/en/dev/ref/settings/#admins
ADMINS = SECRETS.get("DJANGO_ADMINS", [])
# https://docs.djangoproject.com/en/dev/ref/settings/#managers
MANAGERS = ADMINS


# STORAGES
# ------------------------------------------------------------------------------
# https://django-storages.readthedocs.io/en/latest/#installation
INSTALLED_APPS += ["storages"]  # noqa F405
# https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html#settings
AWS_ACCESS_KEY_ID = SECRETS["DJANGO_AWS_ACCESS_KEY_ID"]
# https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html#settings
AWS_SECRET_ACCESS_KEY = SECRETS["DJANGO_AWS_SECRET_ACCESS_KEY"]
# https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html#settings
AWS_STORAGE_BUCKET_NAME = SECRETS["DJANGO_AWS_STORAGE_BUCKET_NAME"]
# https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html#settings
AWS_QUERYSTRING_AUTH = False
# DO NOT change these unless you know what you're doing.
_AWS_EXPIRY = 60 * 60 * 24 * 7
# https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html#settings
AWS_S3_OBJECT_PARAMETERS = {
    "CacheControl": f"max-age={_AWS_EXPIRY}, s-maxage={_AWS_EXPIRY}, must-revalidate"
}
# https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html#settings
AWS_S3_REGION_NAME = SECRETS.get("DJANGO_AWS_S3_REGION_NAME", default="ap-northeast-2")
#  https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html#settings
AWS_DEFAULT_ACL = None


# STATIC
# ------------------------
STATICFILES_STORAGE = "config.settings.production.StaticRootS3Boto3Storage"
STATIC_URL = "/static/"


# MEDIA
# ------------------------------------------------------------------------------
# region http://stackoverflow.com/questions/10390244/
# Full-fledge class: https://stackoverflow.com/a/18046120/104731
from storages.backends.s3boto3 import S3Boto3Storage  # noqa


class StaticRootS3Boto3Storage(S3Boto3Storage):
    location = "static"


class MediaRootS3Boto3Storage(S3Boto3Storage):  # noqa
    location = "media"
    file_overwrite = False


DEFAULT_FILE_STORAGE = "config.settings.production.MediaRootS3Boto3Storage"
MEDIA_URL = "/media/"


# LOGGING
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#logging
# See https://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "verbose": {"format": "%(levelname)s %(asctime)s %(module)s %(message)s"}
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        }
    },
    "loggers": {
        "django.db.backends": {
            "level": "ERROR",
            "handlers": ["console"],
            "propagate": False,
        },
        # Errors logged by the SDK itself
        "sentry_sdk": {"level": "ERROR", "handlers": ["console"], "propagate": False},
        "django.security.DisallowedHost": {
            "level": "ERROR",
            "handlers": ["console"],
            "propagate": False,
        },
    },
}


# Sentry
# ------------------------------------------------------------------------------
SENTRY_DSN = SECRETS["SENTRY_DSN"]
SENTRY_LOG_LEVEL = SECRETS.get("DJANGO_SENTRY_LOG_LEVEL", logging.INFO)

sentry_logging = LoggingIntegration(
    level=SENTRY_LOG_LEVEL  # Capture info and above as breadcrumbs
)

sentry_sdk.init(dsn=SENTRY_DSN, integrations=[sentry_logging, DjangoIntegration()])
