# from django.contrib.auth.models import User
from django.test import TestCase, Client

client = Client()

class TestAll(TestCase):
    def test_get_notice_all(self):
        response = client.get('/notice/all')
        assert response.status_code==200

    def test_get_notice_all_query(self):
        response = client.get('/notice/all?board=cse-main')
        assert response.status_code==200

class TestBoards(TestCase):
    def test_get_notice_main(self):
        response = client.get('/notice/main/')
        assert response.status_code==200

    def test_get_notice_cse(self):
        response = client.get('/notice/cse/')
        assert response.status_code==200
