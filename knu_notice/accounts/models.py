from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    email = models.EmailField(max_length=200, primary_key=True)
    password = models.CharField(max_length=500)
    # device = models.OneToOneField('Device', on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Device(models.Model):
    def __str__(self):
        return id
    id = models.CharField(max_length=200, primary_key=True)
    keywords = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
