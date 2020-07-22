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

class TestBoards(TestCase):
    def test_get_notice_main(self):
        response = client.get('/notice/main')
        assert status.is_success(response.status_code)

    def test_get_notice_cse(self):
        response = client.get('/notice/cse')
        assert status.is_success(response.status_code)

class TestDevices(TestCase):
    @classmethod
    def setUpTestData(cls):
        data = {
            'id':'test',
            'keywords':'keyw',
            'subscriptions':'main',
        }
        response = client.post('/accounts/device', data=data, content_type='application/json')

    def test_accounts_device_post(self):
        data = {
            'id':'post',
            'keywords':'keyw',
            'subscriptions':'main',
        }
        response = client.post('/accounts/device', data=data, content_type='application/json')
        assert status.is_success(response.status_code)

    def test_accounts_device_get(self):
        data = {
            'id':'test',
        }
        response = client.get('/accounts/device', data=data, follow=True)
        assert status.is_success(response.status_code)

    def test_accounts_device_put(self):
        data = {
            'id':'test',
            'keywords':'test',
            'subscriptions':'cse',
        }
        response = client.put('/accounts/device', data=data, content_type='application/json')
        assert status.is_success(response.status_code)

    def test_accounts_device_delete(self):
        data = {
            'id':'test',
        }
        response = client.delete('/accounts/device', data=data, content_type='application/json')
        assert status.is_success(response.status_code)

    def test_get_accounts_device_list(self):
        response = client.get('/accounts/device/list')
        assert status.is_success(response.status_code)