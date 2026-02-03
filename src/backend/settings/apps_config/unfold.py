from django.templatetags.static import static
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from ..base import ADMIN_PATH, PRODUCTION, PROJECT_NAME, env

SITE_NAME = PROJECT_NAME

LINKS = {
    "users": reverse_lazy("admin:core_user_changelist"),
    "groups": reverse_lazy("admin:auth_group_changelist"),
    "country": reverse_lazy("admin:core_country_changelist"),
    "region": reverse_lazy("admin:core_region_changelist"),
    "ideology": reverse_lazy("admin:ideology_ideology_changelist"),
    "association": reverse_lazy("admin:ideology_ideologyassociation_changelist"),
    "religion": reverse_lazy("admin:ideology_religion_changelist"),
    "tag": reverse_lazy("admin:ideology_tag_changelist"),
    "reference": reverse_lazy("admin:ideology_ideologyreference_changelist"),
    "complexity": reverse_lazy(
        "admin:ideology_ideologyabstractioncomplexity_changelist"
    ),
    "section": reverse_lazy("admin:ideology_ideologysection_changelist"),
    "conditioner": reverse_lazy("admin:ideology_ideologyconditioner_changelist"),
    "axis": reverse_lazy("admin:ideology_ideologyaxis_changelist"),
    "completed": reverse_lazy("admin:ideology_completedanswer_changelist"),
    "axis_ans": reverse_lazy("admin:ideology_useraxisanswer_changelist"),
    "cond_ans": reverse_lazy("admin:ideology_userconditioneranswer_changelist"),
    "ideology_axis_def": reverse_lazy(
        "admin:ideology_ideologyaxisdefinition_changelist"
    ),
    "ideology_cond_def": reverse_lazy(
        "admin:ideology_ideologyconditionerdefinition_changelist"
    ),
}

SIDEBAR_NAVIGATION = [
    {
        "title": _("Access Control"),
        "separator": True,
        "items": [
            {"title": _("Users"), "icon": "person", "link": LINKS["users"]},
            {"title": _("Groups"), "icon": "lock", "link": LINKS["groups"]},
        ],
    },
    {
        "title": _("Geography"),
        "separator": True,
        "items": [
            {"title": _("Countries"), "icon": "public", "link": LINKS["country"]},
            {"title": _("Regions"), "icon": "map", "link": LINKS["region"]},
        ],
    },
    {
        "title": _("Ideological Atlas"),
        "separator": True,
        "items": [
            {"title": _("Ideologies"), "icon": "flag", "link": LINKS["ideology"]},
            {
                "title": _("Axis Definitions"),
                "icon": "graphic_eq",
                "link": LINKS["ideology_axis_def"],
            },
            {
                "title": _("Conditioner Definitions"),
                "icon": "playlist_add_check",
                "link": LINKS["ideology_cond_def"],
            },
            {
                "title": _("Associations"),
                "icon": "share_location",
                "link": LINKS["association"],
            },
            {
                "title": _("Religions"),
                "icon": "temple_buddhist",
                "link": LINKS["religion"],
            },
            {"title": _("Tags"), "icon": "label", "link": LINKS["tag"]},
            {
                "title": _("References"),
                "icon": "library_books",
                "link": LINKS["reference"],
            },
        ],
    },
    {
        "title": _("Test Structure"),
        "separator": True,
        "items": [
            {"title": _("Complexities"), "icon": "layers", "link": LINKS["complexity"]},
            {
                "title": _("Sections"),
                "icon": "dashboard_customize",
                "link": LINKS["section"],
            },
            {"title": _("Conditioners"), "icon": "tune", "link": LINKS["conditioner"]},
            {"title": _("Axes"), "icon": "linear_scale", "link": LINKS["axis"]},
        ],
    },
    {
        "title": _("User Data"),
        "separator": True,
        "items": [
            {
                "title": _("Completed Tests"),
                "icon": "assignment_turned_in",
                "link": LINKS["completed"],
            },
            {
                "title": _("Axis Answers"),
                "icon": "analytics",
                "link": LINKS["axis_ans"],
            },
            {
                "title": _("Conditioner Answers"),
                "icon": "fact_check",
                "link": LINKS["cond_ans"],
            },
        ],
    },
]

if not PRODUCTION:
    SIDEBAR_NAVIGATION.append(
        {
            "title": _("Monitoring & Dev"),
            "separator": True,
            "items": [
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
        "show_all_applications": False,
        "navigation": SIDEBAR_NAVIGATION,
    },
    "THEME": "dark",
}
