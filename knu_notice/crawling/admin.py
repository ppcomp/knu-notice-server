from django.contrib import admin
from . import models
from crawling.data import data

admin.site.register(models.Notice)
# models 안에 있는 모델 admin page에 일괄 등록
models_list = []
for key, value in data.items():
    models_list.append(eval(f'models.{key.capitalize()}'))
admin.site.register(models_list)