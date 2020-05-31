# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

from crawling import models

class TestCrawlerPipeline:
    def process_item(self, item, spider):
        # assert False, [item, spider]
        # model = eval(f"models.{item['model']}")
        # model()

        # notice, created = model.objects.get_or_create(
        #     id = item['id'],
        #     defaults={
        #         'title':item['title'],
        #         'link':item['link'],
        #         'date':item['date'],
        #         'author':item['author'],
        #         'reference':item['reference'],
        #     }
        # )
        # if created:
        #     print("new Data insert!")
        return item