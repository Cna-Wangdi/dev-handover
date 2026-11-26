import os

import dj_database_url
from django.core.exceptions import ImproperlyConfigured

from .settings import *

DEBUG = False
SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]
if not SECRET_KEY:
    raise ImproperlyConfigured("DJANGO_SECRET_KEY must be set.")

ALLOWED_HOSTS = [os.environ["RENDER_EXTERNAL_HOSTNAME"]]
DATABASES = {"default": dj_database_url.parse(os.environ["DATABASE_URL"], conn_max_age=60)}
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
CSRF_TRUSTED_ORIGINS = [f"https://{ALLOWED_HOSTS[0]}"]

MIDDLEWARE = [MIDDLEWARE[0], "whitenoise.middleware.WhiteNoiseMiddleware", *MIDDLEWARE[1:]]
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
FRONTEND_DIST = BASE_DIR.parent / "frontend" / "dist"
TEMPLATES[0]["DIRS"] = [FRONTEND_DIST]
WHITENOISE_ROOT = FRONTEND_DIST
ROOT_URLCONF = "config.render_urls"
