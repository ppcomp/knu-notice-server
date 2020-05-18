# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

class CrawlerPipeline:
    def process_item(self, item, spider):
        #get_or_create : 매개변수로 들어오는 데이터를 DB에 있는 데이터와 비교해서 데이터를 Get 하거나 Create 함
        notice, flag = item['model'].objects.get_or_create( bid = item['bid'],
                                                    title = item['title'],
                                                    link = item['link'],
                                                    date = item['date'],
                                                    author = item['author'],
                                                    reference = item['reference'],)
        #flag = True : DB에 저장된 같은 데이터가 없음 (Create)
        #flag = False : DB에 저장된 같은 데이터가 있음 (Get)
        if flag:
            print("new Data insert!")
        return item