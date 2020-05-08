from rest_framework import serializers
from .models import Notice

class NoticeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notice
        fields= (
            'bid',
            'title',
            'link',
            'date',
            'author',
            'reference'
        )
        read_only = ('bid')
