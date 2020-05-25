import os

if os.environ.get('DEV') is True:
    from .dev.celery import app
else:
    from .prod.celery import app