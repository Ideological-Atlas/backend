from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.utils.translation import gettext_lazy as _
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from backend.settings import ADMIN_PATH, PRODUCTION, PROJECT_NAME

admin.site.site_header = _(PROJECT_NAME)
admin.site.site_title = _(PROJECT_NAME)
admin.site.index_title = _("Panel de control")

urlpatterns = (
    [
        path("i18n/", include("django.conf.urls.i18n")),
        path("api/token/login/", TokenObtainPairView.as_view(), name="login"),
        path("api/token/refresh/", TokenRefreshView.as_view(), name="refresh"),
        path("api/token/verify/", TokenVerifyView.as_view(), name="token-verify"),
        path("api/", include("core.api.urls", "core")),
    ]
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    + i18n_patterns(
        path(f"{ADMIN_PATH}/", admin.site.urls),
    )
)

if not PRODUCTION:
    urlpatterns += [
        path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
        path(
            "api/schema/swagger-ui/",
            SpectacularSwaggerView.as_view(url_name="schema"),
            name="swagger-ui",
        ),
        path(
            "api/schema/redoc/",
            SpectacularRedocView.as_view(url_name="schema"),
            name="redoc",
        ),
        path("__debug__/", include("debug_toolbar.urls")),
        path("silk/", include("silk.urls", namespace="silk")),
    ]
