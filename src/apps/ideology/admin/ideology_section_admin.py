from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from ideology.models import IdeologyAxis, IdeologySection, IdeologySectionConditioner
from unfold.admin import ModelAdmin, TabularInline


class IdeologySectionConditionerInline(TabularInline):
    model = IdeologySectionConditioner
    extra = 0
    autocomplete_fields = ["conditioner"]
    verbose_name = _("Condition Rule")
    verbose_name_plural = _("Condition Rules")
    tab = True


class AxisInline(TabularInline):
    model = IdeologyAxis
    extra = 0
    fields = ["name", "left_label", "right_label"]
    tab = True


@admin.register(IdeologySection)
class IdeologySectionAdmin(ModelAdmin):
    list_display = ["name", "abstraction_complexity", "get_condition_count"]
    list_filter_submit = True
    list_filter = ["abstraction_complexity"]
    search_fields = ["name"]
    list_select_related = ["abstraction_complexity"]
    inlines = [IdeologySectionConditionerInline, AxisInline]
    autocomplete_fields = ["abstraction_complexity"]

    @admin.display(description=_("Conditions"))
    def get_condition_count(self, obj):
        return obj.conditioners.count()
