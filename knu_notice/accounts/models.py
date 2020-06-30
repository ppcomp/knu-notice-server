from django.db import models
from django.contrib.auth.models import AbstractUser, AbstractBaseUser
from django.contrib.postgres.fields import ArrayField

class User(AbstractUser):
    device = models.OneToOneField('Device', on_delete=models.SET_NULL, null=True)
    email = models.EmailField(max_length=254, blank=True)

class Device(AbstractBaseUser):
    def __str__(self):
        return f'{self.id_method}-{str(self.id)}'
    id = models.CharField(max_length=200, primary_key=True)
    id_method = models.CharField(max_length=30, default='guid', blank=True)
    keywords = models.CharField(max_length=500, blank=True)
    subscriptions = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
