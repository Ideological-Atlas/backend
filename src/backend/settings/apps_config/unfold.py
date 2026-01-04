from django.templatetags.static import static
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from ..base import ADMIN_PATH, PRODUCTION, PROJECT_NAME, env

SITE_NAME = PROJECT_NAME

SIDEBAR_NAVIGATION = [
    {
        "title": _("Users and groups"),
        "separator": True,
        "items": [
            {
                "title": _("Users"),
                "icon": "person",
                "link": reverse_lazy("admin:core_user_changelist"),
            },
            {
                "title": _("Groups"),
                "icon": "group",
                "link": reverse_lazy("admin:auth_group_changelist"),
            },
        ],
    }
]

if not PRODUCTION:
    SIDEBAR_NAVIGATION.append(
        {
            "title": _("Monitoring & Dev"),
            "separator": True,
            "items": [
                {
                    "title": _("Silk Profiler"),
                    "icon": "speed",
                    "link": reverse_lazy("silk:summary"),
                },
                {
                    "title": _("API Schema (Swagger)"),
                    "icon": "api",
                    "link": reverse_lazy("swagger-ui"),
                },
                {
                    "title": _("API Documentation (Redoc)"),
                    "icon": "description",
                    "link": reverse_lazy("redoc"),
                },
            ],
        }
    )

UNFOLD = {
    "SITE_TITLE": SITE_NAME,
    "SITE_HEADER": SITE_NAME,
    "SITE_SUBHEADER": _(env("PROJECT_SUBHEADER", default="")),
    "SITE_URL": f"/{ADMIN_PATH}/",
    "SITE_ICON": lambda request: static("logo/logo.png"),
    "SITE_FAVICONS": lambda request: [
        {
            "rel": "icon",
            "sizes": "32x32",
            "type": "image/png",
            "href": lambda request: static("logo/logo.png"),
        },
    ],
    "SHOW_LANGUAGES": True,
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
        "navigation": SIDEBAR_NAVIGATION,
    },
}
