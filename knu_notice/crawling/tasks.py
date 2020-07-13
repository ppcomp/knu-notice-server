from __future__ import absolute_import, unicode_literals
import logging, os
from celery import Celery
from celery.schedules import crontab
from billiard.context import Process
from typing import List, Tuple, Dict, TYPE_CHECKING

# from django.conf import settings
from knu_notice.celery import app

import scrapy
from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner
from scrapy.crawler import CrawlerProcess
from scrapy.utils.log import configure_logging
from .crawler.crawler.spiders import crawl_spider
from scrapy.settings import Settings

spiders = [
   # crawl_spider에 게시판 크롤링 class 생성 후 이 곳에 추가.
    # 이 곳에 있는 게시판(class)을 대상으로 crawling됨.
    crawl_spider.MainSpider,
    crawl_spider.CseSpider
    crawl_spider.CbaSpider,
    crawl_spider.BizSpider,
    crawl_spider.AccountSpider,
    crawl_spider.ItSpider,
    crawl_spider.EconomicsSpider,
    crawl_spider.TourismSpider,
]

def get_scrapy_settings():
    scrapy_settings = Settings()
    os.environ['SCRAPY_SETTINGS_MODULE'] = 'crawling.crawler.crawler.settings'
    settings_module_path = os.environ['SCRAPY_SETTINGS_MODULE']
    scrapy_settings.setmodule(settings_module_path, priority='project')
    return scrapy_settings

def crawling_start(scrapy_settings: Settings, spiders: List[object]) -> List[Dict]:
    process = CrawlerProcess(scrapy_settings)
    crawler_list = []
    for spider in spiders:
        crawler = process.create_crawler(spider)
        crawler_list.append(crawler)
        process.crawl(crawler)
    process.start()

    stats_dic_list = []
    for crawler in crawler_list:
        # stats = crawler.stats   # <class 'scrapy.statscollectors.MemoryStatsCollector'>
        stats = crawler.stats.get_stats()   # <class 'dict'>
        stats_dic_list.append(stats)
    return stats_dic_list

@app.task
def crawling():
    scrapy_settings = get_scrapy_settings()
    proc = Process(
        target=crawling_start, 
        args=(
            scrapy_settings,
            spiders,
        )
    )
    proc.start()
    proc.join()