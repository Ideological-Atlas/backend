from django.apps import AppConfig


class IdeologyConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "ideology"

    def ready(self):
        from django.contrib.admin import ModelAdmin

        ModelAdmin.list_per_page = 15
