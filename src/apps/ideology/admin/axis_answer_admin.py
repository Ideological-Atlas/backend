from django.contrib import admin
from ideology.models import UserAxisAnswer
from unfold.admin import ModelAdmin


@admin.register(UserAxisAnswer)
class UserAxisAnswerAdmin(ModelAdmin):
    show_full_result_count = False
    list_per_page = 20
    list_display = ["user", "axis", "value", "is_indifferent", "created"]
    list_filter_submit = True
    list_filter = ["axis__section", "is_indifferent", "created"]
    search_fields = ["user__email", "user__username", "axis__name"]
    autocomplete_fields = ["user", "axis"]
    list_select_related = ["user", "axis"]
    readonly_fields = ["created", "modified"]
