from django.contrib import admin
from ideology.models import UserConditionerAnswer
from unfold.admin import ModelAdmin


@admin.register(UserConditionerAnswer)
class UserConditionerAnswerAdmin(ModelAdmin):
    show_full_result_count = False
    list_per_page = 20
    list_display = ["user", "conditioner", "answer", "uuid", "created"]
    list_filter_submit = True
    list_filter = ["conditioner__type", "created"]
    search_fields = ["user__email", "user__username", "conditioner__name", "uuid"]
    autocomplete_fields = ["user", "conditioner"]
    list_select_related = ["user", "conditioner"]
    readonly_fields = ["created", "modified", "uuid"]
