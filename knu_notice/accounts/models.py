from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager,PermissionsMixin
from django.contrib.postgres.fields import ArrayField

class UserManager(BaseUserManager):    

    use_in_migrations = True

    def create_user(self, id, password=None):
        user = self.model(
            id = id
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    def create_superuser(self, id, password):
        user = self.create_user(
            id = id,
            password=password
        )
        user.is_admin = True
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    def __str__(self):
        ret = ""
        if self.profile:
            ret += f"[{self.profile.nickname}]"
        ret += str(self.id)
        return ret
    class Meta:
        ordering = ['-synched_at']

    objects = UserManager()
    USERNAME_FIELD = 'id'    
    REQUIRED_FIELDS = []

    id = models.CharField(
        max_length=200, 
        primary_key=True, 
        unique=True
    )
    email = models.EmailField(max_length=255, null=True)
    synched_at = models.DateTimeField(auto_now_add=True)
    connected_at = models.DateTimeField(auto_now=True)
    profile = models.OneToOneField('Profile', on_delete=models.CASCADE, null=True)
    device = models.OneToOneField('Device', on_delete=models.SET_NULL, null=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

class Profile(models.Model):
    nickname = models.CharField(
        max_length=200, 
        unique=True
    )
    profile_image = models.URLField(max_length=200, blank=True)
    thumbnail_image_url = models.URLField(max_length=200, blank=True)
    profile_needs_agreement = models.BooleanField(default=False)

class Device(models.Model):
    def __str__(self):
        return str(self.id)
    class Meta:
        ordering = ['-created_at']
    id = models.CharField(max_length=200, primary_key=True)
    id_method = models.CharField(max_length=30, default='InstanceId', blank=True)
    keywords = models.CharField(max_length=500, blank=True)
    subscriptions = models.CharField(max_length=500, blank=True)
    alarm_switch_sub = models.BooleanField(default=False)
    alarm_switch_key = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
