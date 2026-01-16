import multiprocessing
import sys
from os.path import abspath, dirname, join

import environ
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

BASE_DIR = dirname(dirname(abspath(__file__)))
PROJECT_ROOT = dirname(dirname(abspath(__file__)))

env = environ.Env()
environ.Env.read_env(join(PROJECT_ROOT, ".env"))

PROJECT_NAME = env("PROJECT_NAME", default="")

if "test" in sys.argv[1:]:
    try:
        multiprocessing.set_start_method("fork")
    except RuntimeError:
        pass

APPS_DIR = f"{BASE_DIR}/../apps"
SITE_ROOT = dirname(PROJECT_ROOT)
SITE_ID = 1

sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, join(SITE_ROOT, "apps"))
sys.path.insert(0, join(SITE_ROOT, "tests"))

DEBUG = env.bool("DEBUG", False)
DEBUG_SQL = env.bool("DEBUG_SQL", True)
PRODUCTION = env.bool("PRODUCTION", True)
ADMIN_PATH = env("ADMIN_PATH", default="admin")
ENVIRONMENT = env("ENVIRONMENT", default="unknown")

WSGI_APPLICATION = "backend.wsgi.application"

LANGUAGE_CODE = "es-es"
TIME_ZONE = "Europe/Madrid"
timezone.activate(TIME_ZONE)
USE_I18N = True
USE_L10N = True

LANGUAGES = [
    ("es", _("Spanish")),
    ("en", _("English")),
]
MODELTRANSLATION_DEFAULT_LANGUAGE = "es"
MODELTRANSLATION_LANGUAGES = ("es", "en")
LOCALE_PATHS = ("locale",)

STATIC_URL = "/static/"
STATIC_ROOT = "/app/static"
STATICFILES_DIRS = [
    join(BASE_DIR, "static"),
]
MEDIA_URL = "/media/"
MEDIA_ROOT = join(BASE_DIR, "../media")

INTERNAL_APPS = ["core", "ideology"]
THIRD_PARTY_APPS = [
    "modeltranslation",
    "unfold",
    "unfold.contrib.simple_history",
    "storages",
    "simple_history",
    "debug_toolbar",
    "django_extensions",
    "rest_framework",
    "corsheaders",
    "drf_spectacular",
    "rest_framework_simplejwt",
    "axes",
    "silk",
    "cities_light",
]

DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django.contrib.postgres",
    "django.contrib.humanize",
    "django.contrib.sitemaps",
    "django.contrib.admindocs",
]
INSTALLED_APPS = THIRD_PARTY_APPS + DJANGO_APPS + INTERNAL_APPS

MIDDLEWARE = [
    "silk.middleware.SilkyMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "axes.middleware.AxesMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "simple_history.middleware.HistoryRequestMiddleware",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("POSTGRES_DB", default="postgres"),
        "USER": env("POSTGRES_USER", default="postgres"),
        "PASSWORD": env("POSTGRES_PASSWORD", default=""),
        "HOST": env("POSTGRES_HOST", default="postgres"),
        "PORT": env("POSTGRES_PORT", default=""),
        "DISABLE_SERVER_SIDE_CURSORS": True,
        "TEST": {
            "NAME": "testing_database",
        },
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

SUPERUSER_USERNAME = env("SUPERUSER_USERNAME", default=None)
SUPERUSER_EMAIL = env("SUPERUSER_MAIL", default=None)
SUPERUSER_PASSWORD = env("SUPERUSER_PASSWORD", default=None)
