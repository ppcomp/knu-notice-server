from django.db import models
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
            'reference',
            'is_fixed',
        )
        read_only = ('id')

class NoticeSearchSerializer(serializers.ModelSerializer):
    bold_title = serializers.SerializerMethodField()
    class Meta:
        model = Notice
        fields= (
            'id',
            'title',
            'bold_title',
            'link',
            'date',
            'author',
            'reference',
            'is_fixed',
        )
        read_only = ('id')
    def get_bold_title(self, obj):
        return obj.bold_title