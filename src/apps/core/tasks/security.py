from celery import shared_task
from celery.utils.log import get_task_logger
from django.apps import apps
from django.db import transaction

logger = get_task_logger(__name__)


@shared_task
def clear_reset_password_token(user_id):
    User = apps.get_model("core", "User")
    try:
        with transaction.atomic():
            user = User.objects.select_for_update().get(pk=user_id)
            if user.reset_password_uuid:
                user.reset_password_uuid = None
                user.save(update_fields=["reset_password_uuid"])
                logger.info("Reset password token cleared for user %s", user_id)
    except User.DoesNotExist:
        logger.warning("User %s not found during token cleanup", user_id)
