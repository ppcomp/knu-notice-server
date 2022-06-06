"""knu_notice URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.urls import path, include
from django.conf.urls import url

# drf_yasg
from drf_yasg import openapi
from drf_yasg.views import get_schema_view

from knu_notice.utils import IsStaffUser

SCHEMA_VIEW = get_schema_view(
   openapi.Info(
      title="KNU Notice API",
      default_version='v1',
      description="https://play.google.com/store/apps/details?id=com.ppcomp.knu",
      contact=openapi.Contact(email="qwlake@gmail.com"),
      license=openapi.License(name="MIT License"),
   ),
   public=True,
   permission_classes=(IsStaffUser,),
)

urlpatterns = [
    url(r'^swagger/$', login_required(SCHEMA_VIEW.with_ui('swagger', cache_timeout=0))),
    path('admin/', admin.site.urls),
    path('notice/', include('crawling.urls')),
    path('accounts/', include('accounts.urls')),
    path('support/', include('support.urls')),
]
