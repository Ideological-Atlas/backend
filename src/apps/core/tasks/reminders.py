from datetime import timedelta

from celery import shared_task
from core.models import User
from core.tasks.notifications import send_email_notification
from django.utils import timezone


@shared_task
def send_verification_reminders():
    today = timezone.now().date()
    reminders_map = {
        3: "registration_reminder_3_days",
        7: "registration_reminder_7_days",
        30: "registration_reminder_30_days",
    }

    for days_ago, template_name in reminders_map.items():
        target_date = today - timedelta(days=days_ago)

        users = User.objects.filter(is_verified=False, created__date=target_date)

        for user in users:
            send_email_notification.delay(
                to_email=user.email,
                template_name=template_name,
                context={"user_uuid": str(user.uuid)},
                language="es",
            )
