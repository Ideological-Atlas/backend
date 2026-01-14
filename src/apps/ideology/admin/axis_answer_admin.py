from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from ideology.models import AxisAnswer
from unfold.admin import ModelAdmin


@admin.register(AxisAnswer)
class AxisAnswerAdmin(ModelAdmin):
    show_full_result_count = False
    list_per_page = 20

    list_display = ["get_subject", "axis", "value", "is_indifferent", "created"]
    list_filter_submit = True
    list_filter = ["axis__section", "is_indifferent", "created"]
    search_fields = ["user__email", "user__username", "ideology__name", "axis__name"]
    autocomplete_fields = ["user", "ideology", "axis"]
    list_select_related = ["user", "ideology", "axis"]
    readonly_fields = ["created", "modified"]

    @admin.display(description=_("Subject"))
    def get_subject(self, obj):
        if obj.ideology:
            return f"Ideology: {obj.ideology.name}"
        if obj.user:
            return f"User: {obj.user.username}"
        return "-"
