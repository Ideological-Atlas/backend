from celery.schedules import crontab

schedule = {
    "send_verification_reminders_daily": {
        "task": "core.tasks.reminders.send_verification_reminders",
        "schedule": crontab(hour=12, minute=0),
    },
    "delete_unverified_users_daily": {
        "task": "core.tasks.maintenance.delete_unverified_users",
        "schedule": crontab(hour=3, minute=0),
    },
}
