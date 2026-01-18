import json

from django.contrib import admin
from django.db.models import JSONField
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django_json_widget.widgets import JSONEditorWidget
from ideology.models import CompletedAnswer
from unfold.admin import ModelAdmin


@admin.register(CompletedAnswer)
class CompletedAnswerAdmin(ModelAdmin):
    show_full_result_count = False
    list_per_page = 20
    list_display = ["completed_by", "uuid", "answer_hash", "created", "id"]
    list_filter_submit = True
    list_filter = ["created"]
    search_fields = [
        "completed_by__email",
        "completed_by__username",
        "id",
        "uuid",
        "answer_hash",
    ]
    autocomplete_fields = ["completed_by"]
    list_select_related = ["completed_by"]
    readonly_fields = ["created", "modified", "uuid", "answer_hash", "answers_pretty"]

    formfield_overrides = {
        JSONField: {"widget": JSONEditorWidget},
    }

    def answers_pretty(self, obj):
        data = obj.answers
        if not data:
            return "-"
        formatted = json.dumps(data, indent=4, sort_keys=True)
        return format_html(
            '<pre style="color: var(--body-fg); background: var(--bg-primary); padding: 10px; border-radius: 4px; overflow-x: auto;">{}</pre>',
            formatted,
        )

    fieldsets = (
        (None, {"fields": ("completed_by", "uuid", "answer_hash")}),
        (
            _("Data"),
            {
                "fields": (
                    "answers",
                    "answers_pretty",
                ),
                "classes": ("tab-stacked",),
            },
        ),
        (
            _("Timestamps"),
            {"fields": ("created", "modified"), "classes": ("collapse",)},
        ),
    )
