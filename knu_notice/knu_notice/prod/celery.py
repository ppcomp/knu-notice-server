from __future__ import absolute_import, unicode_literals
import os
import logging
from celery import Celery
from celery.signals import setup_logging

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'knu_notice.prod.settings')
app = Celery('knu_notice')
app.config_from_object('django.conf:settings', namespace='CELERY')

@setup_logging.connect
def config_loggers(*args, **kwags):
    from logging.config import dictConfig
    from django.conf import settings
    dictConfig(settings.LOGGING)

app.autodiscover_tasks()