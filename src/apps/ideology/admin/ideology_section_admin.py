from django.contrib import admin
from ideology.models import IdeologyAxis, IdeologySection
from unfold.admin import ModelAdmin, TabularInline


class AxisInline(TabularInline):
    model = IdeologyAxis
    extra = 0
    fields = ["name", "left_label", "right_label", "conditioned_by"]
    tab = True


@admin.register(IdeologySection)
class IdeologySectionAdmin(ModelAdmin):
    list_display = ["name", "abstraction_complexity", "conditioned_by"]
    list_filter_submit = True
    list_filter = ["abstraction_complexity"]
    search_fields = ["name"]
    list_select_related = ["abstraction_complexity", "conditioned_by"]
    inlines = [AxisInline]
    autocomplete_fields = ["abstraction_complexity", "conditioned_by"]
