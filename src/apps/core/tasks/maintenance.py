from datetime import timedelta

from celery import shared_task
from core.models import User
from core.tasks.notifications import send_email_notification
from django.db import transaction
from django.utils import timezone


@shared_task
def delete_unverified_users():
    limit_date = timezone.now() - timedelta(days=31)

    users_to_delete = User.objects.filter(is_verified=False, created__lte=limit_date)

    for user in users_to_delete:
        with transaction.atomic():
            user.delete()
            transaction.on_commit(
                lambda: send_email_notification.delay(
                    to_email=user.email,
                    template_name="user_deleted_due_no_verification",
                    language=user.preferred_language,
                    context={"username": user.username},
                )
            )
