from django.http import HttpResponse
from django.core.validators import ValidationError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import mixins
from rest_framework import generics
from .models import Device
from .serializer import DeviceSerializer

class DeviceList(mixins.ListModelMixin,
                 mixins.CreateModelMixin,
                 mixins.UpdateModelMixin,
                 generics.GenericAPIView):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

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

class DeviceDetail(mixins.RetrieveModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.DestroyModelMixin,
                   generics.GenericAPIView):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
