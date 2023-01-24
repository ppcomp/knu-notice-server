from rest_framework import serializers
from .models import Version, BoardInfo


class NoticeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Version
        fields = (
            'latest',
            'available_version_code',
        )


class BoardInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = BoardInfo
        fields = '__all__'
