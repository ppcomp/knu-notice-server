from __future__ import absolute_import, unicode_literals
import logging
from celery import Celery
from celery.schedules import crontab

from django.conf import settings
from knu_notice.celery import app

logger = logging.getLogger("celery")

@app.task
def show_hello_world():
    logger.info("-"*25)
    logger.info("Printing Hello from Celery")
    logger.info("-"*25)
