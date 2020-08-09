from django.test import TestCase, Client
from rest_framework import status

client = Client()

class TestDevices(TestCase):
    @classmethod
    def setUpTestData(cls):
        data = {
            'id':'test-device-id',
            'keywords':'keyw',
            'subscriptions':'main',
        }
        response = client.post('/accounts/device', data=data, content_type='application/json')

    def test_accounts_device_post(self):
        data = {
            'id':'test',
            'keywords':'keyw',
            'subscriptions':'main',
        }
        response = client.post('/accounts/device', data=data, content_type='application/json')
        assert status.is_success(response.status_code)

    def test_accounts_device_get(self):
        data = {
            'id':'test-device-id',
        }
        response = client.get('/accounts/device', data=data, follow=True)
        assert status.is_success(response.status_code)

    def test_accounts_device_put(self):
        data = {
            'id':'test-device-id',
            'keywords':'test',
            'subscriptions':'cse',
        }
        response = client.put('/accounts/device', data=data, content_type='application/json')
        assert status.is_success(response.status_code)

    def test_accounts_device_delete(self):
        data = {
            'id':'test-device-id',
        }
        response = client.delete('/accounts/device', data=data, content_type='application/json')
        assert status.is_success(response.status_code)

    def test_get_accounts_device_list(self):
        response = client.get('/accounts/device/list')
        assert status.is_success(response.status_code)

class TestUsers(TestCase):
    @classmethod
    def setUpTestData(cls):
        data = {
            'id':'test-device-id',
            'keywords':'keyw',
            'subscriptions':'main',
        }
        response = client.post('/accounts/device', data=data, content_type='application/json')
        data = {
            'id':'test-device-id2',
            'keywords':'keyw',
            'subscriptions':'main',
        }
        response = client.post('/accounts/device', data=data, content_type='application/json')
        data = {
            'id':'test-user-id',
            'email':'email@email.com',
            'device_id':'test-device-id',
        }
        response = client.post('/accounts/user', data=data, content_type='application/json')

    def test_accounts_user_post(self):
        data = {
            'id':'test',
            'email':'email@email.com',
            'device_id':'test-device-id2',
        }
        response = client.post('/accounts/user', data=data, content_type='application/json')
        assert status.is_success(response.status_code)

    def test_accounts_user_get(self):
        data = {
            'id':'test-user-id',
        }
        response = client.get('/accounts/user', data=data, follow=True)
        assert status.is_success(response.status_code)

    def test_accounts_user_put(self):
        data = {
            'id':'test-user-id',
            'email':'email@email.com',
            'device_id':'test-device-id',
        }
        response = client.put('/accounts/user', data=data, content_type='application/json')
        assert status.is_success(response.status_code)

    def test_accounts_user_delete(self):
        data = {
            'id':'test-user-id',
        }
        response = client.delete('/accounts/user', data=data, content_type='application/json')
        assert status.is_success(response.status_code)
