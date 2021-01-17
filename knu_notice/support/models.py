from django.db import models

class Version(models.Model):
    def __str__(self):
        return f'{self.latest} - {self.available_version_code}'
    latest = models.CharField(max_length=20)
    available_version_code = models.IntegerField(default=0)
