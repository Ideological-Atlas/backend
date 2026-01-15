from django.contrib import admin
from django.db.models import JSONField
from ideology.models import CompletedAnswer
from unfold.admin import ModelAdmin
from unfold.contrib.forms.widgets import WysiwygWidget


@admin.register(CompletedAnswer)
class CompletedAnswerAdmin(ModelAdmin):
    show_full_result_count = False
    list_per_page = 20
    list_display = ["completed_by", "uuid", "created", "id"]
    list_filter_submit = True
    list_filter = ["created"]
    search_fields = ["completed_by__email", "completed_by__username", "id", "uuid"]
    autocomplete_fields = ["completed_by"]
    list_select_related = ["completed_by"]
    readonly_fields = ["created", "modified", "uuid"]
    formfield_overrides = {
        JSONField: {
            "widget": WysiwygWidget,
        }
    }
