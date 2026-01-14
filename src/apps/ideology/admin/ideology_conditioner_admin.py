from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from ideology.models import IdeologyConditioner
from modeltranslation.admin import TabbedTranslationAdmin
from unfold.admin import ModelAdmin


@admin.register(IdeologyConditioner)
class IdeologyConditionerAdmin(ModelAdmin, TabbedTranslationAdmin):
    list_display = ["name", "type"]
    list_filter_submit = True
    list_filter = ["type"]
    search_fields = ["name"]
    fieldsets = (
        (None, {"fields": ("name", "description", "type")}),
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
