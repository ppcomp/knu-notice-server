from typing import Dict
from django.core.validators import ValidationError
from rest_framework import serializers
from .models import User, Device
from crawling import models

class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    A ModelSerializer that takes an additional `fields` argument that
    controls which fields should be displayed.
    """

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('fields', None)

        # Instantiate the superclass normally
        super(DynamicFieldsModelSerializer, self).__init__(*args, **kwargs)

        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name)

class DeviceSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Device
        fields= [
            'id',
            'id_method',
            'keywords',
            'subscriptions',
            'alarm_switch',
        ]
        
    def validate(self, attrs):
        if 'subscriptions' in attrs.keys() and attrs['subscriptions'] is not '':
            subscriptions = attrs['subscriptions']
            subscription_list = subscriptions.split('+')
            board_names = set(map(str.lower, models.__dict__.keys()))
            for subscription in subscription_list:
                if subscription not in board_names:
                    raise ValidationError(f"There is no board: '{subscription}'. Please check subscriptions.")
        return attrs

class UserSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = User
        fields= [
            'id',
            'email',
            'device',
        ]

class UserFormSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = User
        fields= [
            'id',
            'email',
            'device_id',
        ]