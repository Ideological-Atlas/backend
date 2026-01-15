from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from ideology.models import IdeologyConditioner, IdeologyConditionerConditioner
from modeltranslation.admin import TabbedTranslationAdmin, TranslationStackedInline
from unfold.admin import ModelAdmin, StackedInline


class IdeologyConditionerConditionerInline(StackedInline, TranslationStackedInline):
    model = IdeologyConditionerConditioner
    extra = 0
    fk_name = "target_conditioner"
    autocomplete_fields = ["source_conditioner"]
    verbose_name = _("Condition Rule")
    verbose_name_plural = _("Condition Rules")
    tab = True


@admin.register(IdeologyConditioner)
class IdeologyConditionerAdmin(ModelAdmin, TabbedTranslationAdmin):
    list_display = ["name", "uuid", "type", "get_condition_count"]
    list_filter_submit = True
    list_filter = ["type"]
    search_fields = ["name", "uuid"]
    readonly_fields = ["created", "modified", "uuid"]
    inlines = [IdeologyConditionerConditionerInline]
    fieldsets = (
        (None, {"fields": ("name", "description", "type", "uuid")}),
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

    @admin.display(description=_("Conditions"))
    def get_condition_count(self, obj):
        return obj.condition_rules.count()
