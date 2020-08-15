from __future__ import absolute_import, unicode_literals
import logging
from celery import Celery
from celery.schedules import crontab, timedelta
from celery.signals import setup_logging
from kombu import Queue

app = Celery(
    'knu_notice',
    broker='redis://redis:6379/0',
    backend='redis://redis:6379/0',
)
app.conf.beat_schedule = {
    # 'cron_crawling': {
    #     'task': 'crawling.tasks.crawling',
    #     'schedule': timedelta(seconds=600),
    #     'args': (1,-1),
    # }
}
app.conf.task_default_queue = 'default'
app.conf.task_queues = (
	Queue('slow_tasks', routing_key='slow.#'),
	Queue('quick_tasks', routing_key='quick.#'),
)

@setup_logging.connect
def config_loggers(*args, **kwags):
    from logging.config import dictConfig
    from django.conf import settings
    dictConfig(settings.LOGGING)

app.autodiscover_tasks()