from django.contrib import admin
from ideology.models import IdeologyAbstractionComplexity
from unfold.admin import ModelAdmin


@admin.register(IdeologyAbstractionComplexity)
class IdeologyAbstractionComplexityAdmin(ModelAdmin):
    list_display = ["complexity", "name", "description"]
    ordering = ["complexity"]
    search_fields = ["name"]
