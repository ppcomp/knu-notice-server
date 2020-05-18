# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

class CrawlerPipeline:
    def process_item(self, item, spider):
        model = item['model'](
            bid = item['bid'],
            title = item['title'],
            link = item['link'],
            date = item['date'],
            author = item['author'],
            reference = item['reference'],
        )
        model.save()
        return item
