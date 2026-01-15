from django.contrib import admin
from ideology.models import IdeologyAbstractionComplexity
from modeltranslation.admin import TabbedTranslationAdmin
from unfold.admin import ModelAdmin


@admin.register(IdeologyAbstractionComplexity)
class IdeologyAbstractionComplexityAdmin(ModelAdmin, TabbedTranslationAdmin):
    list_display = ["complexity", "name", "uuid", "description"]
    ordering = ["complexity"]
    search_fields = ["name", "uuid"]
    readonly_fields = ["created", "modified", "uuid"]
