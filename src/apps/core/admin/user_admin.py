from core.models import User
from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm


@admin.register(User)
class CustomUserAdmin(UserAdmin, ModelAdmin):
    actions = ["send_verification_email"]
    fieldsets = (
        (
            _("Base info"),
            {
                "fields": (
                    "username",
                    "email",
                    "password",
                    "uuid",
                    "verification_uuid",
                    "auth_provider",
                )
            },
        ),
        (
            _("Personal info"),
            {
                "fields": (
                    "first_name",
                    "last_name",
                )
            },
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_verified",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (
            _("Important dates"),
            {"fields": ("last_login", "date_joined", "created", "modified")},
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2", "is_staff"),
            },
        ),
    )
    list_display = [
        "id",
        "uuid",
        "username",
        "email",
        "auth_provider",
        "first_name",
        "last_name",
        "is_staff",
        "is_verified",
    ]
    list_filter = [
        "auth_provider",
        "is_staff",
        "is_superuser",
        "is_active",
        "groups",
    ]
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm
    search_fields = [
        "username",
        "first_name",
        "last_name",
        "email",
        "id",
        "uuid",
        "verification_uuid",
    ]
    readonly_fields = [
        "date_joined",
        "last_login",
        "uuid",
        "verification_uuid",
        "id",
        "created",
        "modified",
        "auth_provider",
    ]
    ordering = ["created"]

    @admin.action(description=_("Send verification email"))
    def send_verification_email(self, request, queryset):
        for user in queryset:
            user.send_verification_email()
        self.message_user(
            request,
            _("Verification emails process started for selected users."),
            messages.SUCCESS,
        )
