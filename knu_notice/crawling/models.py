import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'knu_notice.settings')
from django.db import models

class Notice(models.Model):
    bid = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=100)
    link = models.CharField(max_length=200)
    date = models.DateTimeField()
    author = models.CharField(max_length=30)
    reference = models.CharField(max_length=50,null=True)