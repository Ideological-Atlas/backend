from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from ideology.models import IdeologyConditioner
from unfold.admin import ModelAdmin


@admin.register(IdeologyConditioner)
class IdeologyConditionerAdmin(ModelAdmin):
    list_display = ["name", "type", "abstraction_complexity"]
    list_filter_submit = True
    list_filter = ["type", "abstraction_complexity"]
    search_fields = ["name"]
    list_select_related = ["abstraction_complexity"]
    autocomplete_fields = ["abstraction_complexity"]
    fieldsets = (
        (None, {"fields": ("name", "description", "type", "abstraction_complexity")}),
        (
            _("Configuration"),
            {
                "fields": ("accepted_values",),
                "description": _(
                    'Only required if type is Categorical. Enter a JSON list of strings, e.g., ["Option A", "Option B"]'
                ),
            },
        ),
    )
