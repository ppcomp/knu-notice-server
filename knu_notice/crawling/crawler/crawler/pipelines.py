# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

from crawling import models

class CrawlerPipeline:
    def process_item(self, item, spider):
        model = eval(f"models.{item['model']}")

        #get_or_create: 주어진 매개변수로 생성하려는 모델 객체가 DB에 존재하면 Get, 없으면 Create
        notice, created = model.objects.get_or_create(
            id = item['id'],  # id만 일치하면 기존에 있던 데이터라고 판단.
            defaults={
                'site':item['site'],
                'is_fixed':True if item['is_fixed'] and not item['is_fixed'].isdigit() else False,
                'title':item['title'],
                'link':item['link'],
                'date':item['date'],
                'author':item['author'],
                'reference':item['reference'],
            }
        )
        #created = True: DB에 저장된 같은 데이터가 없음 (Create)
        #created = False: DB에 저장된 같은 데이터가 있음 (Get)
        if created:
            print(f"new Data insert! {item['model']}:{item['title']}")
        return item