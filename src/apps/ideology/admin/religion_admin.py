from django.contrib import admin
from ideology.models import Religion
from unfold.admin import ModelAdmin


@admin.register(Religion)
class ReligionAdmin(ModelAdmin):
    list_display = ["name", "created"]
    search_fields = ["name"]
    readonly_fields = ["created", "modified"]
