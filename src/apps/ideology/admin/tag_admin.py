from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from ideology.models import IdeologyTag, Tag
from modeltranslation.admin import TabbedTranslationAdmin
from unfold.admin import ModelAdmin, StackedInline


class TagAssignmentInline(StackedInline):
    model = IdeologyTag
    extra = 0
    autocomplete_fields = ["ideology"]
    tab = True


@admin.register(Tag)
class TagAdmin(ModelAdmin, TabbedTranslationAdmin):
    list_display = ["name", "uuid", "usage_count", "created"]
    search_fields = ["name", "uuid"]
    inlines = [TagAssignmentInline]
    readonly_fields = ["created", "modified", "uuid"]

    @admin.display(description=_("Usage Count"))
    def usage_count(self, obj):
        return obj.ideology_assignments.count()
