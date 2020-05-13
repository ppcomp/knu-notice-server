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
from .crawler.crawler.spiders.crawl_spider import CrawlSpiderSpider
from scrapy.settings import Settings

settings = Settings()
os.environ['SCRAPY_SETTINGS_MODULE'] = 'crawling.crawler.crawler.settings'
settings_module_path = os.environ['SCRAPY_SETTINGS_MODULE']
settings.setmodule(settings_module_path, priority='project')

def crawling_start():
    process = CrawlerProcess(settings)
    process.crawl(CrawlSpiderSpider)
    process.start()

@app.task
def crawling():
    proc = Process(target=crawling_start)
    proc.start()
    proc.join()