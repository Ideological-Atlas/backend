from django.urls import reverse
from django.utils.html import format_html


def get_admin_path(obj) -> str:
    return reverse(
        f"admin:{obj._meta.app_label}_{obj._meta.model_name}_change", args=[obj.id]
    )


def get_admin_reference(obj):
    path = get_admin_path(obj)
    return format_html('<a href="{}">{}</a>', path, obj)


def get_admin_image(obj, picture_field: str, size: int = 200):
    image_field = getattr(obj, picture_field, None)
    if image_field:
        return format_html(
            '<img src="{}" width="auto" height="{}px" />', image_field.url, size
        )
    return None
