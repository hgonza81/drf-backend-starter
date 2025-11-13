from .base import *  # noqa: F403
from .base import INSTALLED_APPS, REST_FRAMEWORK

# Spectacular configuration for OpenAPI
INSTALLED_APPS += [
    "drf_spectacular",
    "drf_spectacular_sidecar",
]

REST_FRAMEWORK["DEFAULT_SCHEMA_CLASS"] = "drf_spectacular.openapi.AutoSchema"

SPECTACULAR_SETTINGS = {
    "TITLE": "DRF Backend Starter API",
    "DESCRIPTION": "API documentation for DRF backend starter",
    "VERSION": "1.0.0",
}
