from core.api import views as core_views
from django.urls import path

app_name = "core"

urlpatterns = [
    path("register/", core_views.RegisterView.as_view(), name="register"),
    path("me/", core_views.MeDetailView.as_view(), name="me"),
    path(
        "users/verify/<str:uuid>",
        core_views.VerifyUserView.as_view(),
        name="verify_user",
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
