# dev/settings 로부터 재정의

from knu_notice.dev.settings import *

DEBUG = False

WSGI_APPLICATION = 'knu_notice.prod.wsgi.application'

CELERY_BEAT_SCHEDULE = {
    'hello': {
        'task': 'crawling.tasks.crawling',
        'schedule': timedelta(seconds=21600)
    }
}