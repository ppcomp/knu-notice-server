from .settings import *

DEBUG = False

CELERY_BEAT_SCHEDULE = {
    'hello': {
        'task': 'crawling.tasks.crawling',
        'schedule': timedelta(seconds=21600)
    }
}