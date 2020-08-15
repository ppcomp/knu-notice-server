# dev/settings 로부터 재정의

import json

from knu_notice.dev.settings import *

def get_secret(setting):
    with open('resources/secret.json', 'r') as f:
        secret = json.loads(f.read())
    return secret[setting]

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_secret('DJANGO_SECRET_KEY')

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

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': get_secret('DB_NAME'),
        'USER': get_secret('DB_USER'),
        'PASSWORD': get_secret('DB_PASSWORD'),
        'HOST': get_secret('DB_HOST'),
        'PORT': get_secret('DB_PORT'),
    }
}