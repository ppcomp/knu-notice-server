from django.shortcuts import render
from rest_framework import viewsets, status, generics
from rest_framework.permissions import IsAdminUser
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from itertools import chain
from operator import attrgetter

from . import models
from .data import data
from .serializer import NoticeSerializer
from .crawler.crawler.spiders import crawl_spider

@api_view(['GET'])
@permission_classes([IsAdminUser])
def init(request, *arg, **kwarg):
    msg = "Database will be initialized. All board notices are being crawled."
    code = status.HTTP_200_OK
    from crawling import tasks
    if 'board' in kwarg.keys():
        board = f"{kwarg['board'].capitalize()}Spider"
        is_crawled = False
        for i in range(len(tasks.spiders)):
            if tasks.spiders[i].__name__ == board:
                tasks.crawling.apply_async(args=(kwarg['pages'], i), queue='slow_tasks')
                is_crawled = True
                break
        if not is_crawled:
            msg = "Invalid board name. Request with correct board name to initialize Database."
            code = status.HTTP_400_BAD_REQUEST
    else:
        for i in range(len(tasks.spiders)):
            tasks.crawling.apply_async(args=(kwarg['pages'], i), queue='slow_tasks')
    return Response(
        data=msg, 
        status=code
    )

@api_view(['GET'])
def get_board_list(request):
    from crawling import tasks
    ret = []
    for spider in tasks.spiders:
        code = spider.__name__[:spider.__name__.find('Spider')].lower()
        ret.append({
            'name':data[code]['name'],
            'api_url':data[code]['api_url'],
        })
    return Response(ret)

class BoardsList(generics.ListAPIView):
    serializer_class = NoticeSerializer

    def get_queryset(self):
        queryset = models.Notice.objects.all()
        boards = self.request.query_params.get('q', None)
        if boards:
            board_set = set(boards.split())
            queryset = queryset.filter(site__in=board_set)
        return queryset

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