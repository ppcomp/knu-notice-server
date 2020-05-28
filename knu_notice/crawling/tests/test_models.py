# from django.contrib.auth.models import User
from django.test import TestCase, Client
from model_mommy import mommy

from crawling import models

class TestPoint(TestCase):
    def setUp(self):
        self.client = Client()
        self.model_list = []
        for name, cls in models.__dict__.items():
            if isinstance(cls, type):
                self.model_list.append(mommy.make(cls))

    def test_create_models(self):
        for model in self.model_list:
            assert model

    def test_get_notice_all(self):
        response = self.client.get('/notice/all')
        assert response.status_code==200

    def test_get_notice_all_query(self):
        response = self.client.get('/notice/all?board=cse-main')
        assert response.status_code==200