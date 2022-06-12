from collections import defaultdict
from distutils import util
from functools import reduce
import operator

from django.db.models import Q
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, generics
from rest_framework.permissions import IsAdminUser
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from . import models
from .data import data
from .schema import PUSH_SCHEMA, Push
from .serializer import NoticeSerializer

swagger_params = {
    'target': openapi.Parameter('target', openapi.IN_QUERY,
                                description='broadcast | all | (board_code)\nSplit by \'+\'', required=False,
                                type=openapi.TYPE_STRING, default=''),
    'keyword': openapi.Parameter('keyword', openapi.IN_QUERY, description='', required=False, type=openapi.TYPE_STRING,
                                 default=''),
    'deviceId': openapi.Parameter('deviceId', openapi.IN_QUERY, description='', required=False,
                                  type=openapi.TYPE_STRING, default=''),
}


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
    alarm = request.GET.get('alarm', None)
    is_alarm = False if alarm and not util.strtobool(alarm) else True
    if 'board' in kwarg.keys():
        board = f"{kwarg['board'].capitalize()}Spider"
        is_crawled = False
        for i in range(len(spiders.spiders)):
            if spiders.spiders[i].__name__ == board:
                crawling_task.crawling_task.apply_async(args=(kwarg['pages'], i, is_alarm), queue='crawling_tasks')
                is_crawled = True
                break
        if not is_crawled:
            msg = "Invalid board name. Request with correct board name to initialize Database."
            code = status.HTTP_400_BAD_REQUEST
    else:
        crawling_task.crawling_task.apply_async(args=(kwarg['pages'], -1, is_alarm), queue='crawling_tasks')

    return Response(
        data=msg,
        status=code
    )


@swagger_auto_schema(
    method='post',
    request_body=PUSH_SCHEMA
)
@api_view(['POST'])
@permission_classes([IsAdminUser])
def push(request, *arg, **kwarg):
    from crawling.celery_tasks import crawling_task, spiders
    push_schema = Push(**request.data)
    targets: dict[str, list[str]] = {target.code: target.keywords.split('+') for target in push_schema.targets}
    if push_schema.broad_cast:
        msg, code = crawling_task.call_push_alarm(is_broadcast=True, device_ids=push_schema.device_ids)
    else:
        if push_schema.all:
            target_board_code_list = _get_available_boards()
        else:
            target_board_code_list = targets.keys()
        target_board_dic = defaultdict()
        for code in target_board_code_list:
            target_board_dic[code] = set(targets[code])
        msg, code = crawling_task.call_push_alarm(target_board_dic=target_board_dic, device_ids=push_schema.device_ids)
    return Response(
        data=msg,
        status=code
    )


@api_view(['GET'])
def get_board_list(request):
    ret = []
    for code in _get_available_boards():
        ret.append({
            'name': data[code]['name'],
            'api_url': data[code]['api_url'],
        })
    return Response(ret)


class BoardsList(generics.ListAPIView):
    serializer_class = NoticeSerializer
    available_boards = set(_get_available_boards())

    def get_queryset(self):
        orders = ['-date', '-created_at', '-id']
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
            notice_queryset = queryset.filter(reduce(operator.or_, (Q(title__icontains=x) for x in qeurys))).order_by(
                *orders)
        else:
            notice_queryset = queryset.order_by(*orders)
        return notice_queryset
