# -*- coding: utf-8 -*-
from .settings import *

LOG_LEVEL = 'DEBUG'
LOG_FILE = 'scrapy_test.log'

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   'crawling.crawler.crawler.pipelines_test.TestCrawlerPipeline': 300,
}
