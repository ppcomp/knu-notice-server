from __future__ import absolute_import, unicode_literals
import logging, os, json

from billiard import Manager
from billiard.context import Process
from celery import Celery
from celery.schedules import crontab
from celery.result import allow_join_result
from firebase_admin import messaging
from rest_framework import status
import scrapy
from scrapy.crawler import CrawlerRunner
from scrapy.crawler import CrawlerProcess
from scrapy.utils.log import configure_logging
from scrapy.settings import Settings
from typing import List, Tuple, Set, Dict, TYPE_CHECKING

# from django.conf import settings
from knu_notice.celery import app
from .crawler.crawler.spiders import crawl_spider

spiders = [
    # crawl_spider에 게시판 크롤링 class 생성 후 이 곳에 추가.
    # 이 곳에 있는 게시판(class)을 대상으로 crawling됨.
    crawl_spider.MainSpider,
    crawl_spider.CseSpider,
    crawl_spider.CbaSpider,
    # crawl_spider.BizSpider, 
    crawl_spider.AccountSpider,
    crawl_spider.EconomicsSpider,
    # crawl_spider.StatisticsSpider,
    crawl_spider.TourismSpider,
    crawl_spider.ItbSpider,
    # crawl_spider.KnucalsSpider,
    # crawl_spider.CllSpider,
    crawl_spider.BseSpider,
    crawl_spider.FoodtechSpider,
    crawl_spider.AppliedplantSpider,
    crawl_spider.ApplybioSpider,
    crawl_spider.HortiSpider,
    crawl_spider.AgeconSpider,
    crawl_spider.AedSpider,
    crawl_spider.DbeSpider,
    # crawl_spider.EcoenvSpider,
    # crawl_spider.CalsSpider,
    # crawl_spider.AnimalSpider,
    crawl_spider.ApplanimalsciSpider,
    crawl_spider.AniscienceSpider,
    crawl_spider.AceSpider,
    # crawl_spider.ArchitectureSpider,
    crawl_spider.ArchiSpider,
    crawl_spider.CivilSpider,
    crawl_spider.EnvironSpider,
    crawl_spider.MechanicalSpider,
    crawl_spider.MechaSpider,
    crawl_spider.MaterialSpider,
    crawl_spider.EnreSpider,
    crawl_spider.SmeSpider,
    crawl_spider.ChemengSpider,
    crawl_spider.BioengSpider,
    crawl_spider.DesignSpider,
    crawl_spider.KangwonartSpider,
    crawl_spider.SportSpider,
    crawl_spider.VcultureSpider,
    # crawl_spider.EducatioSpider,
    # crawl_spider.HomecsSpider,
    # crawl_spider.ScieduSpider,
    # crawl_spider.EduSpider,
    # crawl_spider.KoreduSpider,
    # crawl_spider.MatheduSpider,
    crawl_spider.HistorySpider,
    # crawl_spider.EngeduSpider,
    # crawl_spider.EthicseduSpider,
    # crawl_spider.SseduSpider,
    # crawl_spider.GeoeduSpider,
    # crawl_spider.PhyeduSpider,
    # crawl_spider.CceduSpider,
    crawl_spider.SocialSpider,
    # crawl_spider.AnthroSpider,
    # crawl_spider.Re1978Spider,
    # crawl_spider.SociologySpider,
    # crawl_spider.MasscomSpider,
    crawl_spider.PoliticsSpider,
    crawl_spider.PadmSpider,
    crawl_spider.PsychSpider,
    crawl_spider.ForestSpider,
    crawl_spider.FmSpider,
    # crawl_spider.ForestrySpider,
    # crawl_spider.FepSpider,
    crawl_spider.WoodSpider,
    # crawl_spider.PaperSpider,
    crawl_spider.LandsSpider,
    # crawl_spider.VetmedSpider,
    crawl_spider.PharmacySpider,
    crawl_spider.NurseSpider,
    # crawl_spider.BmcollegeSpider,
    crawl_spider.MolscienSpider,
    crawl_spider.Bio_healthSpider,
    crawl_spider.BmeSpider,
    crawl_spider.SiSpider,
    crawl_spider.DmbtSpider,
    crawl_spider.ItSpider,
    # crawl_spider.KoreanSpider,
    crawl_spider.EnglishSpider,
    # crawl_spider.FranceSpider,
    crawl_spider.GermanSpider,
    # crawl_spider.ChineseSpider,
    # crawl_spider.JapanSpider,
    crawl_spider.KnuhistoSpider,
    crawl_spider.PhysicsSpider,
    crawl_spider.BiologySpider,
    crawl_spider.MathSpider,
    crawl_spider.GeologySpider,
    crawl_spider.GeophysicsSpider,
    crawl_spider.BiochemSpider,
    # crawl_spider.ChemisSpider,
    crawl_spider.EeeSpider,
    crawl_spider.EeSpider,
    crawl_spider.MultimajorSpider,
    crawl_spider.LiberalSpider,
]

class CustomCrawler:

    def __init__(self):
        self.output = None

    def _yield_output(self, data):
        self.output = data

    def crawling_start(
            self,
            scrapy_settings: Settings, 
            spider: object, 
            board_code: str,
            return_dic: Dict) -> Dict:
        process = CrawlerProcess(scrapy_settings)
        crawler = process.create_crawler(spider)
        process.crawl(crawler, args={'callback': self._yield_output})
        process.start()
        return_dic[board_code] = self.output

        # stats = crawler.stats   # <class 'scrapy.statscollectors.MemoryStatsCollector'>
        stats = crawler.stats.get_stats()   # <class 'dict'>
        return stats

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
            msg = f'List of tokens that caused failures: {failed_tokens}'
            print(msg)
    else:
        msg = "There is no target devices."
    return msg, code

def save_data_to_db(boards_data: Dict[str,List[Dict[str,str]]]) -> List[str]:
    from . import models
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

def get_scrapy_settings() -> Settings:
    scrapy_settings = Settings()
    os.environ['SCRAPY_SETTINGS_MODULE'] = 'crawling.crawler.crawler.settings'
    settings_module_path = os.environ['SCRAPY_SETTINGS_MODULE']
    scrapy_settings.setmodule(settings_module_path, priority='project')
    return scrapy_settings

@app.task
def _single_crawling_task(page_num, spider_idx):
    spider = spiders[spider_idx]
    crawl_spider.page_num = page_num
    manager = Manager()
    return_dic = manager.dict()
    cc = CustomCrawler()
    proc = Process(
        target=cc.crawling_start, 
        args=(
            get_scrapy_settings(),
            spider,
            spider.__name__[:spider.__name__.find('Spider')].lower(),
            return_dic,
        )
    )
    proc.start()
    proc.join()
    return dict(return_dic)

@app.task
def crawling_task(page_num, spider_idx=-1, cron=False):
    if cron:
        from . import models
        fixed_notices = models.Notice.objects.all.filter(is_fixed=True)
        fixed_notices.update(ix_fixed=False)

    res = []
    result_dic = dict()
    if spider_idx == -1:
        for i in range(len(spiders)):
            x = _single_crawling_task.apply_async(args=(page_num, i), queue='single_crawling_tasks')
            res.append(x.collect())
    else:
        res = [_single_crawling_task.apply_async(args=(page_num, spider_idx), queue='single_crawling_tasks')]

    result_dic = dict()
    with allow_join_result():
        for r in res:
            for c in r:
                if c[1]:
                    result_dic.update(c[1])
    
    target_board_code_list = save_data_to_db(result_dic)

    call_push_alarm(target_board_code_list)
