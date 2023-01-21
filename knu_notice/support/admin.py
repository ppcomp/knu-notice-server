from django.contrib import admin
from . import models

admin.site.register(models.Version)
admin.site.register(models.BoardInfo)
