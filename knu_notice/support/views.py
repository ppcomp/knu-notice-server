import json
from rest_framework.response import Response
from rest_framework.decorators import api_view

@api_view(['GET'])
def get_version(request):
    return Response({
        'latest':'9-0.1.7',
        'available_version_code':7,
    })
