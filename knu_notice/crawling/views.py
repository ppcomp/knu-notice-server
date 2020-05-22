from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from . import models
from .data import data
from .serializer import NoticeSerializer

class NoticeViewSet(viewsets.ModelViewSet):
    queryset = models.Notice.objects.all()
    serializer_class = NoticeSerializer
    def perform_create(self, serializer):
        serializer.save()

class MainViewSet(NoticeViewSet):
    queryset = models.Main.objects.all()
    
class CseViewSet(NoticeViewSet):
    queryset = models.Cse.objects.all()

@api_view(['GET'])
def get_board_list(request):
    print(request)
    ret = []
    for value in data.values():
        ret.append({
            'name':value['name'],
            'api_url':value['api_url'],
        })
    return Response(ret)