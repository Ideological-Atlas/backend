import os
import sys

from kombu import Exchange, Queue

from .celery_beat_schedule import schedule

TESTING = "test" in sys.argv

task_default_queue = "default"
task_queues = (Queue("default", Exchange("default"), routing_key="default"),)

if TESTING:
    broker_url = "memory://"
else:
    broker_url = f'amqp://{os.getenv("RABBITMQ_DEFAULT_USER")}:{os.getenv("RABBITMQ_DEFAULT_PASS")}@{os.getenv("BROKER_HOST")}:5672'

broker_pool_limit = 10
broker_connection_timeout = 60
broker_heartbeat = 30

broker_transport_options = {
    "max_retries": 3,
    "interval_start": 0,
    "interval_step": 0.2,
    "interval_max": 0.2,
}

task_always_eager = TESTING
task_eager_propagates = TESTING
task_publish_retry = True
worker_disable_rate_limits = False
task_acks_late = True

task_serializer = "json"
result_serializer = "json"
accept_content = ["application/json"]

worker_hijack_root_logger = False
worker_prefetch_multiplier = 1
worker_max_tasks_per_child = 1000

worker_send_task_events = True
task_send_sent_event = True

beat_schedule = schedule
timezone = "Europe/Madrid"
