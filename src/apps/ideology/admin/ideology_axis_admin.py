from django.contrib import admin
from ideology.models import IdeologyAxis
from unfold.admin import ModelAdmin


@admin.register(IdeologyAxis)
class IdeologyAxisAdmin(ModelAdmin):
    list_display = ["name", "section", "left_label", "right_label", "conditioned_by"]
    list_filter_submit = True
    list_filter = ["section__abstraction_complexity", "section"]
    search_fields = ["name", "section__name"]
    list_select_related = ["section", "conditioned_by"]
    autocomplete_fields = ["section", "conditioned_by"]
