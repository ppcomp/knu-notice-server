from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from itertools import chain
from operator import attrgetter

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
def get_board_all(request):
    try:
        board_list = request.query_params.get('board').split("-")
        objs = []
        for board in board_list:
            objs.append(data[board]['model'].objects.all())
        ret = sorted(
            list(chain(*objs)),
            key=attrgetter('date')
        )
        serialized = NoticeSerializer(ret, many=True)
    except: # query params가 없을때. 모든 notice 반환
        serialized = NoticeSerializer(
            models.Notice.objects.all(), 
            many=True,
        )
    return Response(serialized.data)

@api_view(['GET'])
def get_board_list(request):
    ret = []
    for value in data.values():
        ret.append({
            'name':value['name'],
            'api_url':value['api_url'],
        })
    return Response(ret)