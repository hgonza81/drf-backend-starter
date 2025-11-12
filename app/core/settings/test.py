from .base import *  # noqa: F403

DEBUG = False
TESTING = True

DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}
