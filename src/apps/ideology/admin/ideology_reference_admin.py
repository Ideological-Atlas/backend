from django.contrib import admin
from ideology.models import IdeologyReference
from modeltranslation.admin import TabbedTranslationAdmin
from unfold.admin import ModelAdmin


@admin.register(IdeologyReference)
class IdeologyReferenceAdmin(ModelAdmin, TabbedTranslationAdmin):
    list_display = ["name", "ideology", "url"]
    search_fields = ["name", "ideology__name", "description"]
    list_filter_submit = True
    list_filter = ["ideology"]
    autocomplete_fields = ["ideology"]
    list_select_related = ["ideology"]
