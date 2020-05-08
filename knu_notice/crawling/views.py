from django.shortcuts import render
from rest_framework import viewsets

from .models import Notice, Main, Cse
from .serializer import NoticeSerializer

class NoticeViewSet(viewsets.ModelViewSet):
    queryset = Notice.objects.all()
    serializer_class = NoticeSerializer
    def perform_create(self, serializer):
        serializer.save()

class MainViewSet(NoticeViewSet):
    queryset = Main.objects.all()
    
class CseViewSet(NoticeViewSet):
    queryset = Cse.objects.all()