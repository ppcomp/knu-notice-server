import os
from django.db import models

from crawling.data import data

class Notice(models.Model):
    id = models.CharField(max_length=30, primary_key=True)
    title = models.CharField(max_length=100)
    link = models.CharField(max_length=200)
    date = models.DateTimeField()
    author = models.CharField(max_length=30)
    reference = models.CharField(max_length=50,null=True)

    class Meta:
          ordering = ['-date']  # 기본 정렬: 시간 내림차순(최신 우선)

    def __str__(self):
        return self.title

'''
class Main(Notice):
    pass
'''
# 위와 같은 형식의 모델이 data로부터 자동 생성
for key, item in data.items():
    txt = f"""
class {key.capitalize()}(Notice):
    pass
"""
    exec(compile(txt,"<string>","exec"))