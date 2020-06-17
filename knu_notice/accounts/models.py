from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    device = models.OneToOneField('Device', on_delete=models.SET_NULL, null=True)
    email = models.EmailField(max_length=254, blank=True)

class Device(models.Model):
    def __str__(self):
        return self.id
    id = models.CharField(max_length=200, primary_key=True)
    keywords = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
