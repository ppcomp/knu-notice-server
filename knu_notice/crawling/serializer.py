from rest_framework import serializers
from .models import Notice

class NoticeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notice
        fields= (
            'id',
            'title',
            'link',
            'date',
            'author',
            'reference'
        )
        read_only = ('id')