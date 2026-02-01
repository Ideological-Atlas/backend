from django.contrib import admin
from ideology.models import IdeologyAxisDefinition, IdeologyConditionerDefinition
from unfold.admin import ModelAdmin


@admin.register(IdeologyAxisDefinition)
class IdeologyAxisDefinitionAdmin(ModelAdmin):
    list_display = [
        "ideology",
        "axis",
        "value",
        "is_indifferent",
        "created",
    ]
    list_filter_submit = True
    list_filter = ["ideology", "axis__section", "is_indifferent"]
    search_fields = ["ideology__name", "axis__name"]
    autocomplete_fields = ["ideology", "axis"]
    list_select_related = ["ideology", "axis"]
    readonly_fields = ["created", "modified", "uuid"]


@admin.register(IdeologyConditionerDefinition)
class IdeologyConditionerDefinitionAdmin(ModelAdmin):
    list_display = ["ideology", "conditioner", "answer", "created"]
    list_filter_submit = True
    list_filter = ["ideology", "conditioner"]
    search_fields = ["ideology__name", "conditioner__name", "answer"]
    autocomplete_fields = ["ideology", "conditioner"]
    list_select_related = ["ideology", "conditioner"]
    readonly_fields = ["created", "modified", "uuid"]
