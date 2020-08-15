from django.contrib.postgres.search import SearchHeadline, SearchQuery, SearchVector
from django.db.models.query import QuerySet
from django.shortcuts import render
import firebase_admin
from firebase_admin import credentials
from firebase_admin import messaging
from firebase_admin import datetime
from rest_framework import viewsets, status, generics
from rest_framework.permissions import IsAdminUser
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from itertools import chain
from operator import attrgetter

from accounts import models as accounts_models
from . import models
from .crawler.crawler.spiders import crawl_spider
from .data import data
from .serializer import NoticeSerializer, NoticeSearchSerializer

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
def push(request, *arg, **kwarg):
    msg = "Push success."
    code = status.HTTP_200_OK

    registration_tokens = list(accounts_models.Device.objects
        .all()
        .filter()
        .values_list('id', flat=True)
    )

    message = messaging.MulticastMessage(
        data={'score': '850', 'time': '2:45'},
        tokens=registration_tokens,
        android=messaging.AndroidConfig(
            priority='normal',
            notification=messaging.AndroidNotification(
                title='테스트 타이틀',
                body='테스트 바디',
                icon='',
                color='#f45342',
                sound='default' # 이거 없으면 백그라운드 수신시 소리, 진동, 화면켜짐 x
            ),
        ),
    )
    response = messaging.send_multicast(message)

    if response.failure_count > 0:
        responses = response.responses
        failed_tokens = []
        for idx, resp in enumerate(responses):
            if not resp.success:
                # The order of responses corresponds to the order of the registration tokens.
                failed_tokens.append(registration_tokens[idx])
        code = status.HTTP_400_BAD_REQUEST
        msg = f'List of tokens that caused failures: {failed_tokens}'

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
