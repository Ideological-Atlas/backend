from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from ideology.models import Ideology, IdeologyAssociation, IdeologyReference
from modeltranslation.admin import TabbedTranslationAdmin, TranslationTabularInline
from unfold.admin import ModelAdmin, TabularInline


class IdeologyAssociationInline(TabularInline):
    model = IdeologyAssociation
    extra = 0
    autocomplete_fields = ["country", "region", "religion"]
    verbose_name = _("Association")
    verbose_name_plural = _("Associations")
    tab = True


class IdeologyReferenceInline(TabularInline, TranslationTabularInline):
    model = IdeologyReference
    extra = 0
    verbose_name = _("Reference")
    verbose_name_plural = _("References")
    tab = True


@admin.register(Ideology)
class IdeologyAdmin(ModelAdmin, TabbedTranslationAdmin):
    list_display = ["name", "created", "modified", "get_association_count"]
    search_fields = ["name", "description_supporter"]
    list_filter_submit = True
    list_filter = ["created"]
    inlines = [IdeologyAssociationInline, IdeologyReferenceInline]
    readonly_fields = ["created", "modified", "uuid"]
    fieldsets = (
        (
            _("General Info"),
            {
                "fields": ("name", "color", "flag", "background"),
            },
        ),
        (
            _("Descriptions"),
            {
                "fields": (
                    "description_supporter",
                    "description_detractor",
                    "description_neutral",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            _("System"),
            {
                "fields": ("created", "modified", "uuid"),
                "classes": ("collapse",),
            },
        ),
    )

    @admin.display(description=_("Associations count"))
    def get_association_count(self, obj):
        return obj.associations.count()
