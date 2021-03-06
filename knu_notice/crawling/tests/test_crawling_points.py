from django.test import TestCase, Client
from rest_framework import status

client = Client()

class TestAll(TestCase):
    def test_get_notice_all(self):
        response = client.get('/notice/all')
        assert status.is_success(response.status_code)

    def test_get_notice_all_query(self):
        response = client.get('/notice/all?q=cse+main')
        assert status.is_success(response.status_code)

class TestSearch(TestCase):
    def test_get_notice_search(self):
        response = client.get('/notice/search?q=장학금')
        assert status.is_success(response.status_code)