from __future__ import absolute_import, unicode_literals
from collections import defaultdict
import time, logging, os, json
from typing import List, Tuple, Set, Dict, DefaultDict, TYPE_CHECKING

from celery import group
from celery.result import allow_join_result
from firebase_admin import messaging
from rest_framework import status
import scrapy

from knu_notice.celery import app
from .spiders import spiders
from .single_crawling_task import single_crawling_task

@app.task
def crawling_task(page_num, spider_idx=-1, cron=False):
    print(f"{time.strftime('%y-%m-%d %H:%M:%S')} crawling_task started.")
    if cron:
        from crawling import models    # lazy import
        fixed_notices = models.Notice.objects.all().filter(is_fixed=True)
        fixed_notices.update(is_fixed=False)

    # res = []
    result_dic = dict()
    if spider_idx == -1:
        for i in range(len(spiders)):
            result_dic.update(single_crawling_task(page_num, i))
    else:
        result_dic.update(single_crawling_task(page_num, spider_idx))
    
    print(f"{time.strftime('%y-%m-%d %H:%M:%S')} save_data_to_db started.")
    target_board_dic = save_data_to_db(result_dic)

    print(f"{time.strftime('%y-%m-%d %H:%M:%S')} call_push_alarm started.")
    call_push_alarm(target_board_dic)

def save_data_to_db(boards_data: Dict[str,List[Dict[str,str]]]) -> DefaultDict[str,set]:
    from crawling import models
    target_board_dic = defaultdict(set)
    notice_id_list = []
    for board_code, item_list in boards_data.items():
        model = eval(f"models.{board_code.capitalize()}")
        for item in item_list:
            is_fixed = True if item['is_fixed'] and not item['is_fixed'].isdigit() else False
            notice, created = model.objects.get_or_create(
                id = item['id'],  # id만 일치하면 기존에 있던 데이터라고 판단.
                defaults={
                    'site':item['site'],
                    'is_fixed':is_fixed,
                    'title':item['title'],
                    'link':item['link'],
                    'date':item['date'],
                    'author':item['author'],
                    'reference':item['reference'],
                }
            )
            #created = True: DB에 저장된 같은 데이터가 없음 (Create)
            #created = False: DB에 저장된 같은 데이터가 있음 (Get)
            if created:
                target_board_dic[item['site']].add(item['title'])
                print(f"new Data insert! {item['site']}:{item['title']}")
            else:
                if notice.is_fixed != is_fixed:
                    notice_id_list.append(item['id'])
    models.Notice.objects.all().filter(id__in=set(notice_id_list)).update(is_fixed=True)
    return target_board_dic

def get_target_tokens():
    pass    

def call_push_alarm(
    target_board_dic: DefaultDict[str,set] = defaultdict(set),
    is_broadcast: bool=False,
    data=dict(),
    title='새 공지가 추가되었습니다.',
    body='지금 어플을 열어 확인해 보세요!') -> Tuple[str,str]:
    from accounts import models as accounts_models
    from crawling.data import data as board_data
    
    msg = "Push success."
    code = status.HTTP_200_OK

    broadcast_tokens = []
    subscription_tokens = dict()
    keyword_tokens = dict()
    if is_broadcast:
        target_device_list = list(accounts_models.Device.objects.all()
            .filter(alarm_switch=True)
            .values_list('id', flat=True)
        )
        broadcast_tokens = target_device_list
    else:
        target_board_code_set = set(target_board_dic.keys())
        devices = accounts_models.Device.objects.all().exclude(alarm_switch=False)
        for device in devices:
            subscriptions_set = set(device.subscriptions.split('+'))
            target_list = list(subscriptions_set & target_board_code_set)
            if target_list:
                subscription_tokens[device.id] = ' · '.join(list(map(lambda x: board_data[x]['name'], target_list)))

            # orders = ['-date','-created_at','-id']
            # notice_queryset = queryset.filter(reduce(operator.or_, (Q(title__icontains=x) for x in qeurys))).order_by(*orders)
            # keywords_set = set(device.keywords.split('+'))

    if subscription_tokens:
        '''
        Condition:
        1. is_broadcast=False
        2. 알람을 켜고, 새 글이 올라온 학과를 구독중인 디바이스(subscription_tokens)가 존재할때

        messaging.send_all() -> Maximum target: 500
        https://firebase.google.com/docs/cloud-messaging/send-message?hl=ko#send-a-batch-of-messages
        '''
        messages = []
        reg_keys = list(subscription_tokens.keys())
        reg_values = list(subscription_tokens.values())
        for device_id, to_body in zip(reg_keys, reg_values):
            messages.append(
                messaging.Message(
                    data=data,
                    token=device_id,
                    notification=messaging.Notification(title=title, body=to_body),
                    android=messaging.AndroidConfig(priority='high')
                )
            )
        check_fcm_response(messaging.send_all(messages), reg_keys)
    elif broadcast_tokens:
        '''
        Condition:
        1. is_broadcast=True
        2. 알람을 킨 디바이스(broadcast_tokens)가 존재할때

        Maximum target: 100
        https://firebase.google.com/docs/reference/admin/dotnet/class/firebase-admin/messaging/multicast-message
        '''
        message = messaging.MulticastMessage(
            data=data,
            tokens=broadcast_tokens,
            notification=messaging.Notification(title=title, body=body),
            android=messaging.AndroidConfig(priority='normal')
        )
        check_fcm_response(messaging.send_multicast(message), broadcast_tokens)
    else:
        msg = "There is no target devices."
    return msg, code

def check_fcm_response(response, tokens):
    if response.failure_count > 0:
        responses = response.responses
        failed_tokens = []
        for idx, resp in enumerate(responses):
            if not resp.success:
                # The order of responses corresponds to the order of the registration tokens.
                failed_tokens.append(tokens[idx])
        msg = f'List of tokens that caused failures: {failed_tokens}'
        print(msg)