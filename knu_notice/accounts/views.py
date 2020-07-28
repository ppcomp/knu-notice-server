import json
from django.http import HttpResponse, Http404
from django.core.validators import ValidationError
from rest_framework import status, mixins, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from .models import Device, User
from . import serializer

def get_object(model, pk):
    try:
        return model.objects.get(pk=pk)
    except model.DoesNotExist:
        raise Http404

def get_json_data(request):
    data = request.body.decode('utf-8')
    if not data:
        raise Exception("Request body is empty.")
    json_data = json.loads(data)
    return json_data

# 개발 전용
class DeviceList(mixins.ListModelMixin,
                 mixins.CreateModelMixin,
                 mixins.UpdateModelMixin,
                 generics.GenericAPIView):
    queryset = Device.objects.all()
    serializer_class = serializer.DeviceSerializer

    # permission_classes = [IsAdminUser,] # 활성화시 admin 계정만 접근 가능
    # authentication_classes = [JSONWebTokenAuthentication,] # 활성화시 admin 계정만 접근 가능

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

class Account(generics.GenericAPIView):

    model = None

    def get(self, request, *args, **kwargs):
        id = request.query_params.get('id')
        obj = get_object(self.model, id)
        serializer = self.get_serializer(obj)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        json_data = get_json_data(request)
        obj = get_object(self.model, json_data['id'])
        serializer = self.get_serializer(obj, data=json_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        json_data = get_json_data(request)
        obj = get_object(self.model, json_data['id'])
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class DeviceView(Account):

    serializer_class = serializer.DeviceSerializer
    model = Device


class UserView(Account):

    serializer_class = serializer.UserFormSerializer
    model = User

    def get_serializer(self, *args, **kwargs):
        return serializer.UserSerializer(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        json_data = get_json_data(request)
        device = get_object(Device, str(json_data['device_id']))
        json_data['device'] = device
        serializer = self.get_serializer(data=json_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
