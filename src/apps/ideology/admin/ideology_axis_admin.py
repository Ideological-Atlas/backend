from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from ideology.models import IdeologyAxis, IdeologyAxisConditioner
from modeltranslation.admin import TabbedTranslationAdmin, TranslationTabularInline
from unfold.admin import ModelAdmin, TabularInline


class IdeologyAxisConditionerInline(TabularInline, TranslationTabularInline):
    model = IdeologyAxisConditioner
    extra = 0
    autocomplete_fields = ["conditioner"]
    verbose_name = _("Condition Rule")
    verbose_name_plural = _("Condition Rules")
    tab = True


@admin.register(IdeologyAxis)
class IdeologyAxisAdmin(ModelAdmin, TabbedTranslationAdmin):
    list_display = [
        "name",
        "section",
        "left_label",
        "right_label",
        "get_condition_count",
    ]
    list_filter_submit = True
    list_filter = ["section__abstraction_complexity", "section"]
    search_fields = ["name", "section__name"]
    list_select_related = ["section"]
    autocomplete_fields = ["section"]
    inlines = [IdeologyAxisConditionerInline]

    @admin.display(description=_("Conditions"))
    def get_condition_count(self, obj):
        return obj.conditioners.count()
