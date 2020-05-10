# -*- coding: utf-8 -*-
import scrapy
#from crawler.items import CrawlerItem

class CrawlSpiderSpider(scrapy.Spider):
    name = 'crawl_spider'
    #allowed_domains = ['https://cse.kangwon.ac.kr/index.php?mp=5_1_1']
    start_urls = ['https://cse.kangwon.ac.kr/index.php?mp=5_1_1']

    def bid_split(self, x):
        idx = x.find("BID")+4
        for i in range(idx, idx+100000):
            if x[i] == "&":
                return x[idx:i]

    def parse(self, response):
        url = response.xpath('//*[@id="bbsWrap"]/table/tbody/tr/td[2]/a').extract()
        titles = response.xpath('//*[@id="bbsWrap"]/table/tbody/tr/td[2]/a/text()').extract()
        date = response.xpath('//*[@id="bbsWrap"]/table/tbody/tr/td[4]/text()').extract()
        author = response.xpath('//*[@id="bbsWrap"]/table/tbody/tr/td[3]/text()').extract()
        

        for item in zip(url, titles, date, author):
            # data_set = CrawlerItem()
            # data_set['bid'] = self.bid_split(item[0].strip())
            # data_set['title'] = item[1].strip()
            # data_set['link'] = item[0].strip()
            # data_set['date'] = item[2].strip()
            # data_set['author'] = item[3].strip()
            scrapyed_info = {
                'bid' : self.bid_split(item[0].strip()),
                'title' : item[1].strip(),
                'link' : item[0].strip(),
                'date' : item[2].strip(),
                'author' : item[3].strip(),
            }
            yield scrapyed_info
