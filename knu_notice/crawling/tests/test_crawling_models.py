# from django.contrib.auth.models import User
from django.test import TestCase, Client
from model_mommy import mommy

from crawling import models

class TestModels(TestCase):
    def setUp(self):
        self.model_list = []
        for name, cls in models.__dict__.items():
            if isinstance(cls, type):
                self.model_list.append(mommy.make(cls))

    def test_create_models(self):
        for model in self.model_list:
            assert model
