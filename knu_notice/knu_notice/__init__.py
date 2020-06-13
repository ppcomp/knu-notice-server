import os

if os.environ.get('DEV') == 'True':
    from .dev.celery import app as celery_app
else:
    from .prod.celery import app as celery_app

__all__ = ['celery_app']