from rest_framework import serializers
from .models import Version
from crawling import models

class NoticeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Version
        fields= (
            'latest',
            'available_version_code',
        )