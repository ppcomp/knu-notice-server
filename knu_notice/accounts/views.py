from django.http import HttpResponse
from django.core.validators import ValidationError
from rest_framework import status
from rest_framework import mixins
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from .models import Device
from .serializer import DeviceSerializer

# 개발 전용
class DeviceList(mixins.ListModelMixin,
                 mixins.CreateModelMixin,
                 mixins.UpdateModelMixin,
                 generics.GenericAPIView):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

class DeviceDetail(mixins.RetrieveModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.DestroyModelMixin,
                   generics.GenericAPIView):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        serializer = self.get_serializer()
        try:
            validated_data = serializer.validate(request.data)
            device, created = Device.objects.update_or_create(
                id=validated_data.get('id', None),
                defaults={'keywords': validated_data.get('keywords', None)}
            )
        except ValidationError as e:
            return Response(e, status=status.HTTP_400_BAD_REQUEST)
        if created:
            return Response('Device registerd on server.', status=status.HTTP_201_CREATED)
        else:
            return Response('Keywords modified.', status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
