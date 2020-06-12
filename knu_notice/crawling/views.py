from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from itertools import chain
from operator import attrgetter

from . import models
from .data import data
from .serializer import NoticeSerializer

@api_view(['GET'])
def get_board_list(request):
    ret = []
    for value in data.values():
        ret.append({
            'name':value['name'],
            'api_url':value['api_url'],
        })
    return Response(ret)

@api_view(['GET'])
def get_board_all(request):
    try:
        board_list = request.query_params.get('q').split("+")
        objs = []
        for board in board_list:
            # ex) txt = models.main.objects.all()
            txt = f"models.{data[board]['model']}.objects.all()"
            objs.append(eval(txt))
        ret = sorted(
            list(chain(*objs)),
            key=attrgetter('date')
        )
        serialized = NoticeSerializer(ret, many=True)
    except: 
        # query params가 없을때. 모든 notice 반환
        serialized = NoticeSerializer(
            models.Notice.objects.all(), 
            many=True,
        )
    return Response(serialized.data)

@api_view(['GET'])
def get_board(request, board:str):
    try:
        board_title = board.title()
        # ex) txt = models.main.objects.all()
        txt = f"models.{board_title}.objects.all()"
        serialized = NoticeSerializer(eval(txt), many=True)
        return Response(serialized.data)
    except:
        raise NotFound(detail="Error 404, invalid board name", code=404)