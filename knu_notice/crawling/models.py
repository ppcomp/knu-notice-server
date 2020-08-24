import os
from django.db import models
from django.db.models import Q, F
from django.contrib.postgres.search import SearchQuery, Value, Func

from crawling.data import data

class Headline(Func):
    function = 'ts_headline'

    def __init__(self, field, query, config=None, options=None, **extra):
        expressions = [field, query]
        if config:
            expressions.insert(0, Value(config))
        if options:
            expressions.append(Value(options))
        extra.setdefault('output_field', models.TextField())
        super().__init__(*expressions, **extra)

class NoticeManager(models.Manager):
    def search(self, search_text):
        search_query = SearchQuery(search_text)
        qs = (
            self.get_queryset()
            .filter(Q(title__icontains=search_text))
            .annotate(bold_title=Headline(F('title'), search_query))
        )
        return qs

class Notice(models.Model):
    objects = NoticeManager()
    id = models.CharField(max_length=200, primary_key=True)
    site = models.CharField(max_length=30)
    is_fixed = models.BooleanField(default=False)
    title = models.CharField(max_length=200)
    link = models.CharField(max_length=500)
    date = models.DateField(null=True)
    author = models.CharField(max_length=30, null=True)
    reference = models.CharField(max_length=50, null=True)

    class Meta:
        ordering = ['-is_fixed', '-date']  # 기본 정렬: 고정 공지 우선, 시간 내림차순(최신 우선)

    def __str__(self):
        return self.title

"""
class Main(Notice):
    pass
"""
# 위와 같은 형식의 모델이 data로부터 자동 생성
for key, item in data.items():
    txt = f"""
class {key.capitalize()}(Notice):
    pass
"""
    exec(compile(txt,"<string>","exec"))