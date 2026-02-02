from core.models import Country, Region
from django.contrib import admin
from modeltranslation.admin import TabbedTranslationAdmin
from unfold.admin import ModelAdmin


@admin.register(Country)
class CountryAdmin(ModelAdmin, TabbedTranslationAdmin):
    list_display = ["name", "code2", "uuid"]
    search_fields = ["name", "code2"]


@admin.register(Region)
class RegionAdmin(ModelAdmin, TabbedTranslationAdmin):
    list_display = ["name", "country", "uuid"]
    search_fields = ["name", "country__name"]
    list_filter = ["country"]
    autocomplete_fields = ["country"]
