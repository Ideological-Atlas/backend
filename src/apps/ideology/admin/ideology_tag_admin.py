from django.contrib import admin
from ideology.models import IdeologyTag
from unfold.admin import ModelAdmin


@admin.register(IdeologyTag)
class IdeologyTagAdmin(ModelAdmin):
    list_display = ["tag", "ideology", "uuid"]
    search_fields = ["tag__name", "ideology__name", "uuid"]
    list_filter_submit = True
    list_filter = ["tag", "ideology"]
    autocomplete_fields = ["tag", "ideology"]
    list_select_related = ["tag", "ideology"]
    readonly_fields = ["created", "modified", "uuid"]
