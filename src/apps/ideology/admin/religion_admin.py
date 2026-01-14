from django.contrib import admin
from ideology.models import Religion
from modeltranslation.admin import TabbedTranslationAdmin
from unfold.admin import ModelAdmin


@admin.register(Religion)
class ReligionAdmin(ModelAdmin, TabbedTranslationAdmin):
    list_display = ["name", "created"]
    search_fields = ["name"]
    readonly_fields = ["created", "modified"]
