from .base import *  # noqa: F403
from .base import BASE_DIR

DEBUG = False
TESTING = True

# DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR.parent.parent / "db-test.sqlite3",
    }
}
