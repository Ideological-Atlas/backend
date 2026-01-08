from django.contrib import admin
from ideology.models import IdeologyAssociation
from unfold.admin import ModelAdmin


@admin.register(IdeologyAssociation)
class IdeologyAssociationAdmin(ModelAdmin):
    list_display = ["ideology", "country", "region", "religion"]
    list_filter_submit = True
    list_filter = ["ideology", "country", "religion"]
    search_fields = ["ideology__name", "country__name", "religion__name"]
    autocomplete_fields = ["ideology", "country", "region", "religion"]
    list_select_related = ["ideology", "country", "region", "religion"]
