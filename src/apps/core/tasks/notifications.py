from typing import Any, Optional

import requests
from celery import shared_task
from celery.utils.log import get_task_logger
from django.conf import settings

logger = get_task_logger(__name__)


@shared_task(bind=True, max_retries=3)
def send_email_notification(
    self,
    to_email: str,
    template_name: str,
    context: Optional[dict[str, Any]] = None,
    language: str = "es",
) -> dict[str, Any]:
    try:
        url = f"{settings.NOTIFICATIONS_SERVICE_URL}/notifications/send"
        payload = {
            "to_email": to_email,
            "template_name": template_name,
            "language": language,
            "context": context or {},
        }
        logger.debug("Sending notification to %s with payload: %s", url, payload)
        response = requests.post(
            url=url,
            json=payload,
            headers={"Authorization": "Bearer " + settings.NOTIFICATIONS_API_KEY},
            timeout=5,
        )
        if not response.ok:
            logger.error(
                "Notification Service Error [%s]: %s",
                response.status_code,
                response.text,
            )
        response.raise_for_status()
        logger.info("Notification sent successfully to %s", to_email)
        return response.json()
    except requests.exceptions.RequestException as exc:
        logger.error("Network/Connection error sending to %s: %s", to_email, exc)
        raise self.retry(exc=exc, countdown=2**self.request.retries)
