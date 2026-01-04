from django.templatetags.static import static
from django.urls import reverse_lazy

from ..base import ADMIN_PATH, PROJECT_NAME, env

SITE_NAME = PROJECT_NAME

UNFOLD = {
    "SITE_TITLE": SITE_NAME,
    "SITE_HEADER": SITE_NAME,
    "SITE_SUBHEADER": env("PROJECT_SUBHEADER", default=""),
    "SITE_URL": f"/{ADMIN_PATH}/",
    "SITE_LOGO": lambda request: static("logo/logo.png"),
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
        "navigation": [
            {
                "title": "Users and groups",
                "separator": True,
                "items": [
                    {
                        "title": "Users",
                        "icon": "person",
                        "link": reverse_lazy("admin:core_user_changelist"),
                    },
                    {
                        "title": "Groups",
                        "icon": "group",
                        "link": reverse_lazy("admin:auth_group_changelist"),
                    },
                ],
            }
        ],
    },
}
