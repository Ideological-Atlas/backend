from django.utils.translation import gettext_lazy as _

from ..base import PROJECT_NAME, env

ROOT_URLCONF = "backend.urls"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication"
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
    "PAGE_SIZE": 25,
}

SPECTACULAR_SETTINGS = {
    "TITLE": f"{PROJECT_NAME} API",
    "DESCRIPTION": _(
        f"Complete documentation of the {PROJECT_NAME} API. "
        "Here you can explore the available endpoints, authentication methods, "
        "and data structures."
    ),
    "VERSION": env("API_VERSION", default="1.0.0"),
    "SERVE_INCLUDE_SCHEMA": False,
    "CONTACT": {
        "name": f"{PROJECT_NAME} Team",
        "email": env("SUPPORT_EMAIL", default=""),
    },
    "LICENSE": {
        "name": "MIT License",
    },
    "TAGS": [
        {
            "name": "auth",
            "description": _("Authentication, registration and token management."),
        },
        {
            "name": "users",
            "description": _("User profile and verification operations."),
        },
        {
            "name": "geography",
            "description": _("Countries and regions data."),
        },
        {
            "name": "structure",
            "description": _("Test structure definition (axes, conditioners, etc)."),
        },
        {
            "name": "ideologies",
            "description": _("Ideologies catalog and details."),
        },
        {
            "name": "answers",
            "description": _("User answers and results processing."),
        },
    ],
    "COMPONENT_SPLIT_REQUEST": True,
}
