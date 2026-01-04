from .base import env

SECRET_KEY = env.get("DJANGO_SECRET_KEY")
ALLOWED_HOSTS = env.get("BACKEND_ALLOWED_HOSTS", "").split(",")
CORS_ALLOWED_ORIGINS = env.get("CORS_ALLOWED_ORIGINS", "").split(",")
CSRF_TRUSTED_ORIGINS = env.get("CSRF_TRUSTED_ORIGINS", "").split(",")

X_FRAME_OPTIONS = "SAMEORIGIN"

AUTH_USER_MODEL = "core.User"
AUTHENTICATION_BACKENDS = [
    "axes.backends.AxesBackend",
    "core.auth_backends.EmailOrUsernameModelBackend",
    "django.contrib.auth.backends.ModelBackend",
]

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": int(env.get("PASSWORD_MIN_LENGTH", 7))},
    },
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
