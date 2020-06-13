from typing import Dict
from django.core.validators import ValidationError
from rest_framework import serializers
from .models import User, Device
from crawling import models

class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields= [
            'id',
            'keywords',
        ]
        
    def validate(self, attrs):
        keywords = attrs['keywords']
        board_names = models.__dict__.keys()
        k_list = keywords.split('+')
        for k in k_list:
            if k.title() not in board_names:
                raise ValidationError(f"There is no board: '{k}'. Please check keywords.")
        return attrs