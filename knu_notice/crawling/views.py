from django.contrib.postgres.search import SearchHeadline, SearchQuery, SearchVector
from django.db.models.query import QuerySet
from django.shortcuts import render
import firebase_admin
from rest_framework import viewsets, status, generics
from rest_framework.permissions import IsAdminUser
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from itertools import chain
from operator import attrgetter

from accounts import models as accounts_models
from . import models
from .data import data
from .serializer import NoticeSerializer, NoticeSearchSerializer

@api_view(['GET'])
@permission_classes([IsAdminUser])
def init(request, *arg, **kwarg):
    msg = "Database will be initialized. All board notices are being crawled."
    code = status.HTTP_200_OK
    from crawling.tasks import crawling_task, spiders
    if 'board' in kwarg.keys():
        board = f"{kwarg['board'].capitalize()}Spider"
        is_crawled = False
        for i in range(len(spiders.spiders)):
            if spiders.spiders[i].__name__ == board:
                crawling_task.crawling_task.apply_async(args=(kwarg['pages'], i), queue='crawling_tasks')
                is_crawled = True
                break
        if not is_crawled:
            msg = "Invalid board name. Request with correct board name to initialize Database."
            code = status.HTTP_400_BAD_REQUEST
    else:
        crawling_task.crawling_task.apply_async(args=(kwarg['pages'], -1), queue='crawling_tasks')

    return Response(
        data=msg, 
        status=code
    )

@api_view(['GET'])
@permission_classes([IsAdminUser])
def push(request, *arg, **kwarg):
    from crawling.tasks import crawling_task, spiders
    targets = request.query_params.get('target', None)
    if targets=='broadcast':
        msg, code = crawling_task.call_push_alarm(is_broadcast=True)
    else:
        if targets=='all':
            target_board_code_list = models.Notice.objects.all().values_list('site', flat=True)
        elif targets:
            target_board_code_list = targets.split()
        else:
            target_board_code_list = []
        msg, code = crawling_task.call_push_alarm(target_board_code_list=target_board_code_list)
    return Response(
        data=msg, 
        status=code
    )

@api_view(['GET'])
def get_board_list(request):
    from crawling.tasks import spiders
    ret = []
    for spider in spiders.spiders:
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

class SearchList(generics.ListAPIView):
    serializer_class = NoticeSearchSerializer

    def get_queryset(self):
        qeurys = self.request.query_params.get('q', None)
        target = self.request.query_params.get('target', None)
        queryset = models.Notice.objects.all()
        if target and target != 'all':
            board_set = set(target.split())
            queryset = queryset.filter(site__in=board_set)

        if qeurys:
            query = SearchQuery(qeurys)
            notice_queryset = queryset.annotate(
                bold_title=SearchHeadline(
                    'title',
                    query,
                    start_sel='<u><strong>',
                    stop_sel='</strong></u>',
                )
            ).filter(bold_title__contains='<u><strong>')
        else:
            notice_queryset = QuerySet()
        return notice_queryset
