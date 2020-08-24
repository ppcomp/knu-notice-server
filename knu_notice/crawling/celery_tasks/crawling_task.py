from __future__ import absolute_import, unicode_literals
import time, logging, os, json
from typing import List, Tuple, Set, Dict, TYPE_CHECKING

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
    target_board_code_list = save_data_to_db(result_dic)

    print(f"{time.strftime('%y-%m-%d %H:%M:%S')} call_push_alarm started.")
    call_push_alarm(target_board_code_list)

def save_data_to_db(boards_data: Dict[str,List[Dict[str,str]]]) -> List[str]:
    from crawling import models
    target_board_code_set = set()
    for board_code, item_list in boards_data.items():
        model = eval(f"models.{board_code.capitalize()}")
        for item in item_list:
            notice, created = model.objects.get_or_create(
                id = item['id'],  # id만 일치하면 기존에 있던 데이터라고 판단.
                defaults={
                    'site':item['site'],
                    'is_fixed':True if item['is_fixed'] and not item['is_fixed'].isdigit() else False,
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
                target_board_code_set.add(item['site'])
                print(f"new Data insert! {item['site']}:{item['title']}")
            else:
                if notice.is_fixed != item['is_fixed']:
                    notice.is_fixed = item['is_fixed']
    return list(target_board_code_set)

def call_push_alarm(
    target_board_code_list: List[str]=[],
    is_broadcast: bool=False,
    data=dict(),
    title='새 공지가 추가되었습니다.',
    body='지금 어플을 열어 확인해 보세요!') -> Tuple[str,str]:
    from accounts import models as accounts_models
    
    msg = "Push success."
    code = status.HTTP_200_OK

    registration_tokens = []
    if is_broadcast:
        target_device_list = list(accounts_models.Device.objects.all()
            .filter(alarm_switch=True)
            .values_list('id', flat=True)
        )
        registration_tokens = target_device_list
    else:
        token_set = set()
        for board_code in target_board_code_list:
            tokens = list(accounts_models.Device.objects
                .all()
                .exclude(alarm_switch=False)
                .filter(subscriptions__contains=board_code)
                .values_list('id', flat=True)
            )
            token_set.update(tokens)
        registration_tokens = list(token_set)

    if len(registration_tokens) != 0:
        message = messaging.MulticastMessage(
            data=data,
            tokens=registration_tokens,
            android=messaging.AndroidConfig(
                priority='normal',
                notification=messaging.AndroidNotification(
                    title=title,
                    body=body,
                    sound='default'
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
            msg = f'List of tokens that caused failures: {failed_tokens}'
            print(msg)
    else:
        msg = "There is no target devices."
    return msg, code