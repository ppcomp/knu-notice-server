# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))))
import scrapy
from scrapy_djangoitem import DjangoItem
from crawling.models import Notice
#scrapy.Item
class CrawlerItem(DjangoItem):
    # define the fields for your item here like:
    # name = scrapy.Field()
    django_model = Notice
    pass
