# from django.contrib.auth.models import User
import os
from django.test import TestCase, Client
from model_mommy import mommy
from scrapy.settings import Settings

from crawling import models
from crawling.tasks import crawling_start

class TestModels(TestCase):
    def setUp(self):
        self.scrapy_settings = Settings()
        os.environ['SCRAPY_SETTINGS_MODULE'] = 'crawling.crawler.crawler.settings_test'
        settings_module_path = os.environ['SCRAPY_SETTINGS_MODULE']
        self.scrapy_settings.setmodule(settings_module_path, priority='project')
        
    def test_crawler(self):
        assert crawling_start(self.scrapy_settings)