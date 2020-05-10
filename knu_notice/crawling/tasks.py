from __future__ import absolute_import, unicode_literals
import logging
from celery import Celery
from celery.schedules import crontab

from django.conf import settings
from knu_notice.celery import app

import scrapy
from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from .crawler.crawler.spiders.crawl_spider import CrawlSpiderSpider
from scrapy.utils.project import get_project_settings
logger = logging.getLogger("celery")

@app.task
def crawling():
    configure_logging()
    runner = CrawlerRunner()
    runner.crawl(CrawlSpiderSpider)
    d = runner.join()
    d.addBoth(lambda _: reactor.stop())

    reactor.run()