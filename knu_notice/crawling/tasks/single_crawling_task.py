from __future__ import absolute_import, unicode_literals
import logging, os, json
from typing import List, Tuple, Set, Dict, TYPE_CHECKING

from billiard import Manager
from billiard.context import Process
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from knu_notice.celery import app
from crawling.crawler.crawler.spiders import crawl_spider
from .spiders import spiders

@app.task
def single_crawling_task(page_num, spider_idx):
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

def get_scrapy_settings() -> Settings:
    scrapy_settings = Settings()
    os.environ['SCRAPY_SETTINGS_MODULE'] = 'crawling.crawler.crawler.settings'
    settings_module_path = os.environ['SCRAPY_SETTINGS_MODULE']
    scrapy_settings.setmodule(settings_module_path, priority='project')
    return scrapy_settings