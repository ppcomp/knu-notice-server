from collections import defaultdict
from distutils import util
from functools import reduce
import operator

from django.contrib.postgres.search import SearchHeadline, SearchQuery, SearchVector
from django.db.models import Q
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
from .serializer import NoticeSerializer

def _get_available_boards():
    from crawling.celery_tasks import spiders
    ret = []
    for spider in spiders.spiders:
        code = spider.__name__[:spider.__name__.find('Spider')].lower()
        ret.append(code)
    return ret

@api_view(['GET'])
@permission_classes([IsAdminUser])
def init(request, *arg, **kwarg):
    msg = "Database will be initialized. All board notices are being crawled."
    code = status.HTTP_200_OK
    from crawling.celery_tasks import crawling_task, spiders
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
    from crawling.celery_tasks import crawling_task, spiders
    targets = request.query_params.get('target', None)
    if targets=='broadcast':
        msg, code = crawling_task.call_push_alarm(is_broadcast=True)
    else:
        if targets=='all':
            target_board_code_list = _get_available_boards()
        elif targets:
            target_board_code_list = targets.split()
        else:
            target_board_code_list = []
        target_board_dic = defaultdict()
        for code in target_board_code_list:
            target_board_dic[code] = set()
        msg, code = crawling_task.call_push_alarm(target_board_dic=target_board_dic)
    return Response(
        data=msg, 
        status=code
    )

@api_view(['GET'])
def get_board_list(request):
    ret = []
    for code in _get_available_boards():
        ret.append({
            'name':data[code]['name'],
            'api_url':data[code]['api_url'],
        })
    return Response(ret)

class BoardsList(generics.ListAPIView):
    serializer_class = NoticeSerializer
    available_boards = set(_get_available_boards())

    def get_queryset(self):
        orders = ['-date','-created_at','-id']
        qeurys = self.request.query_params.get('q', None)
        target = self.request.query_params.get('target', 'all')
        is_fixed = self.request.query_params.get('fixed', 'false')
        queryset = models.Notice.objects.all().filter(site__in=self.available_boards)
        
        if util.strtobool(is_fixed):
            orders.insert(0, '-is_fixed')
        if target != 'all':
            board_set = set(target.split())
            queryset = queryset.filter(site__in=board_set).order_by(*orders)

        if qeurys:
            qeurys = set(qeurys.split())
            notice_queryset = queryset.filter(reduce(operator.or_, (Q(title__icontains=x) for x in qeurys))).order_by(*orders)
        else:
            notice_queryset = queryset.order_by(*orders)
        return notice_queryset
