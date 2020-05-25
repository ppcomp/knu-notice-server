from django.contrib import admin
from . import models

# models 안에 있는 모델 admin page에 일괄 등록
models_list = []
for name, cls in models.__dict__.items():
    if isinstance(cls, type):
        models_list.append(cls)
admin.site.register(models_list)