from __future__ import absolute_import, unicode_literals
import logging, os
from celery import Celery
from celery.schedules import crontab
from billiard.context import Process

# from django.conf import settings
from knu_notice.celery import app

import scrapy
from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner
from scrapy.crawler import CrawlerProcess
from scrapy.utils.log import configure_logging
from .crawler.crawler.spiders import crawl_spider
from scrapy.settings import Settings

settings = Settings()
os.environ['SCRAPY_SETTINGS_MODULE'] = 'crawling.crawler.crawler.settings'
settings_module_path = os.environ['SCRAPY_SETTINGS_MODULE']
settings.setmodule(settings_module_path, priority='project')
spiders = [
    # crawl_spider에 게시판 크롤링 class 생성 후 이 곳에 추가.
    # 이 곳에 있는 게시판(class)을 대상으로 crawling됨.
    crawl_spider.MainSpider,
    crawl_spider.CseSpider,
]

def crawling_start():
    process = CrawlerProcess(settings)
    for spider in spiders:
        process.crawl(spider)
    process.start()

@app.task
def crawling():
    proc = Process(target=crawling_start)
    proc.start()
    proc.join()