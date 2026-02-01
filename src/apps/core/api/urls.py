from core.api import views as core_views
from django.urls import path

app_name = "core"

urlpatterns = [
    path("register/", core_views.RegisterView.as_view(), name="register"),
    path("login/google/", core_views.GoogleLoginView.as_view(), name="google-login"),
    path(
        "users/verify/<str:verification_uuid>/",
        core_views.VerifyUserView.as_view(),
        name="verify_user",
    ),
    path(
        "password/reset/request/",
        core_views.PasswordResetRequestView.as_view(),
        name="password-reset-request",
    ),
    path(
        "password/reset/verify/<str:uuid>/",
        core_views.PasswordResetVerifyTokenView.as_view(),
        name="password-reset-verify-token",
    ),
    path(
        "password/reset/confirm/<str:uuid>/",
        core_views.PasswordResetConfirmView.as_view(),
        name="password-reset-confirm",
    ),
    path("me/", core_views.MeDetailView.as_view(), name="me"),
    path("me/password/", core_views.UserSetPasswordView.as_view(), name="set-password"),
    path(
        "users/affinity/<str:uuid>/",
        core_views.UserAffinityView.as_view(),
        name="user-affinity",
    ),
    path(
        "users/affinity/ideology/<str:uuid>/",
        core_views.UserIdeologyAffinityView.as_view(),
        name="user-ideology-affinity",
    ),
    path(
        "geography/countries/",
        core_views.CountryListView.as_view(),
        name="country-list",
    ),
    path(
        "geography/regions/",
        core_views.RegionListView.as_view(),
        name="region-list",
    ),
]
