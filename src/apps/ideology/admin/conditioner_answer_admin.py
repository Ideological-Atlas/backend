from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from ideology.models import ConditionerAnswer
from unfold.admin import ModelAdmin


@admin.register(ConditionerAnswer)
class ConditionerAnswerAdmin(ModelAdmin):
    show_full_result_count = False
    list_per_page = 20

    list_display = ["get_subject", "conditioner", "answer", "created"]
    list_filter_submit = True
    list_filter = ["conditioner__type", "created"]
    search_fields = [
        "user__email",
        "user__username",
        "ideology__name",
        "conditioner__name",
    ]
    autocomplete_fields = ["user", "ideology", "conditioner"]
    list_select_related = ["user", "ideology", "conditioner"]
    readonly_fields = ["created", "modified"]

    @admin.display(description=_("Subject"))
    def get_subject(self, obj):
        if obj.ideology:
            return f"Ideology: {obj.ideology.name}"
        if obj.user:
            return f"User: {obj.user.username}"
        return "-"
