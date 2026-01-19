from core.models import User
from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm


@admin.register(User)
class CustomUserAdmin(UserAdmin, ModelAdmin):
    actions = [
        "send_verification_email",
        "trigger_password_reset",
        "trigger_password_reset_silent",
    ]
    actions_detail = [
        "trigger_password_reset",
        "trigger_password_reset_silent",
        "send_verification_email",
    ]

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
                    "reset_password_uuid",
                    "auth_provider",
                )
            },
        ),
        (
            _("Personal info"),
            {"fields": ("first_name", "last_name", "bio")},
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
    ]
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm
    search_fields = [
        "username",
        "first_name",
        "last_name",
        "email",
        "bio",
        "id",
        "uuid",
        "verification_uuid",
    ]
    readonly_fields = [
        "date_joined",
        "last_login",
        "uuid",
        "verification_uuid",
        "reset_password_uuid",
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

    def _perform_password_reset(
        self, request, queryset, send_notification, success_message
    ):
        for user in queryset:
            user.initiate_password_reset(send_notification=send_notification)
        self.message_user(request, success_message, messages.SUCCESS)

    @admin.action(description=_("Trigger password reset (Send Email)"))
    def trigger_password_reset(self, request, queryset):
        self._perform_password_reset(
            request,
            queryset,
            send_notification=True,
            success_message=_(
                "Password reset initiated with email for selected users."
            ),
        )

    @admin.action(description=_("Trigger password reset (Silent - No Email)"))
    def trigger_password_reset_silent(self, request, queryset):
        self._perform_password_reset(
            request,
            queryset,
            send_notification=False,
            success_message=_(
                "Password reset token generated silently. No email sent."
            ),
        )
