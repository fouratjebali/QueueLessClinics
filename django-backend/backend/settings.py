from __future__ import annotations

import os
from pathlib import Path

from django.core.management.utils import get_random_secret_key
from corsheaders.defaults import default_headers


# ---------------------------------------------------------------------------
# Base directory
# ---------------------------------------------------------------------------
# The root of the project directory tree. Files such as ``manage.py`` live
# one level above this settings module. ``Path(__file__).resolve()`` points
# to ``<base_dir>/queueless_backend/settings.py``.
BASE_DIR = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# Secret key & debug
# ---------------------------------------------------------------------------
# ``SECRET_KEY`` is used by Django for cryptographic signing. In
# production this value must be kept secret! If no environment
# variable is provided a new random key is generated on each boot. To
# avoid regenerating keys in development set ``DJANGO_SECRET_KEY`` in
# your shell.
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', get_random_secret_key())

# Toggle debug mode using the ``DEBUG`` environment variable.
# Accept common truthy values so ``DEBUG=1`` or ``DEBUG=true`` both work.
DEBUG = os.getenv('DEBUG', 'True').lower() in {'true', '1', 'yes', 'on'}

# Hosts allowed to connect. In a containerised deployment this is often
# provided as a comma‑separated list (e.g. ``localhost,127.0.0.1,backend``).
raw_allowed_hosts = os.getenv('ALLOWED_HOSTS', '')
if raw_allowed_hosts:
    ALLOWED_HOSTS: list[str] = [
        host.strip()
        for host in raw_allowed_hosts.replace(';', ',').split(',')
        if host.strip()
    ]
else:
    ALLOWED_HOSTS = []


# ---------------------------------------------------------------------------
# Application definitions
# ---------------------------------------------------------------------------
# Core Django apps are required for the admin, authentication, sessions
# and staticfiles. ``rest_framework`` adds API support. ``core`` is
# our application containing business logic and database models.
INSTALLED_APPS: list[str] = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third‑party
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    # Optional: PostgreSQL specific fields like ArrayField
    'django.contrib.postgres',
    # Local apps
    'core',
]


MIDDLEWARE: list[str] = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'backend.wsgi.application'


# ---------------------------------------------------------------------------
# Database configuration
# ---------------------------------------------------------------------------
# Use PostgreSQL by default. Values come from environment variables with
# sensible defaults so the app can run both locally and in Docker. The
# docker‑compose file provides ``DB_HOST``, ``DB_PORT``, ``DB_NAME``,
# ``DB_USER`` and ``DB_PASSWORD`` which are all honoured here.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME", "queueless_clinic"),
        "USER": os.getenv("DB_USER", "queueless_admin"),
        "PASSWORD": os.getenv("DB_PASSWORD", "QueueLess2026!Secure"),
        "HOST": os.getenv("DB_HOST", "localhost"),
        "PORT": os.getenv("DB_PORT", "5432"),
    }
}


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------
# We define a custom user model in ``core.models.User``. Using a custom
# user model is necessary to store clinic and role information and to
# authenticate users via e‑mail addresses. ``AUTH_USER_MODEL`` tells
# Django which model to use.
AUTH_USER_MODEL = 'core.User'


# ---------------------------------------------------------------------------
# Internationalisation & localisation
# ---------------------------------------------------------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = os.getenv('TIME_ZONE', 'Africa/Tunis')  # default to the user's locale
USE_I18N = True
USE_TZ = True


# ---------------------------------------------------------------------------
# Static & media files
# ---------------------------------------------------------------------------
# Static files (CSS, JavaScript, images) are served from ``STATIC_URL``.
# In production ``STATIC_ROOT`` should point to the directory where
# ``collectstatic`` places files. For user uploaded content you can
# define ``MEDIA_URL`` and ``MEDIA_ROOT``. See Django docs for details.
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# ---------------------------------------------------------------------------
# Django REST Framework configuration
# ---------------------------------------------------------------------------
# For this project we expose a public API without server‑side auth
# enforcement; authentication and authorisation are handled at the
# application level. All endpoints are accessible anonymously unless a
# view overrides the permission classes explicitly.
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_PAGINATION_CLASS': None,
}


# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
raw_cors_origins = os.getenv('CORS_ALLOWED_ORIGINS', '')
if raw_cors_origins:
    CORS_ALLOWED_ORIGINS = [
        origin.strip()
        for origin in raw_cors_origins.replace(';', ',').split(',')
        if origin.strip()
    ]
else:
    CORS_ALLOW_ALL_ORIGINS = True

CORS_ALLOW_HEADERS = list(default_headers) + [
    'x-user-role',
    'x-user-id',
    'x-user-email',
]


# ---------------------------------------------------------------------------
# Default primary key field type
# ---------------------------------------------------------------------------
# Use UUIDs for all models by default. This prevents collisions and
# ensures predictable IDs across distributed systems. Individual
# models explicitly define their primary key fields but this setting
# ensures any unspecified model fields default to BigAutoField.
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'