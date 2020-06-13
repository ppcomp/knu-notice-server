import os

if os.environ.get('DEV') == 'True':
    from .dev.celery import app
else:
    from .prod.celery import app