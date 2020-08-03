# dev/settings 로부터 재정의

from knu_notice.dev.settings import *

DEBUG = False

WSGI_APPLICATION = 'knu_notice.prod.wsgi.application'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': u'[%(levelname)s|%(filename)s:%(lineno)s] %(asctime)s > %(message)s'
        },
    },
    'handlers': {
        'console_celery': {
            'level': 'ERROR',
            'class': 'logging.StreamHandler',
            'formatter': 'default'
        },
        'file_celery': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'celery.log',
            'formatter': 'default',
            'maxBytes': 1024 * 1024 * 100,  # 100 mb
        },
    },
    'loggers': {
        'celery': {
            'handlers': ['file_celery', 'console_celery'],
            'level': 'DEBUG',
        },
    }
}