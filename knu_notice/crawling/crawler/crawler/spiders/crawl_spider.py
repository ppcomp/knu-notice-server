# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor

'''
1. 각 class 구동시 필요한 import 구문은 class 안에 있어야 함.
 (scrapy에서 class만 갖고 crawling 하기 때문에 class 밖에 적어 놓으면 인식 불가.)
2. 비고(reference)가 없는 게시판이라면 xpath를 None으로 지정할 것.
3. set_args() 함수의 bid 인자는 각 게시판에서 게시물을 구별할때 사용되는 키 값.
 (ex cse 게시판은 BID 사용, main 게시판은 nttNo 사용)
'''

class DefaultSpider(scrapy.Spider):

    def set_args(self, model, bid, url_xpath, titles_xpath, dates_xpath, authors_xpath, references_xpath):
        self.model = model
        self.bid = bid
        self.url_xpath = url_xpath
        self.titles_xpath = titles_xpath
        self.dates_xpath = dates_xpath
        self.authors_xpath = authors_xpath
        self.references_xpath = references_xpath

    def bid_split(self, url):
        idx = url.find(self.bid)+len(self.bid)+1
        for i in range(idx, len(url)):
            if url[i] == "&":
                return url[idx:i]
        return url[idx:]

    def remove_null(self, items):
        ret = []
        x = ''
        for item in items:
            x = item.strip()
            if x != '':
                ret.append(x)
        return ret

    def parse(self, response):
        url_form = LinkExtractor(restrict_xpaths=self.url_xpath,attrs='href')
        urls = url_form.extract_links(response)
        titles = self.remove_null(response.xpath(self.titles_xpath).extract())
        dates = self.remove_null(response.xpath(self.dates_xpath).extract())
        authors = self.remove_null(response.xpath(self.authors_xpath).extract())
        if self.references_xpath:
            references = self.remove_null(response.xpath(self.references_xpath).extract())
        else:
            references = [None for _ in range(len(urls))]
        for item in zip(urls, titles, dates, authors, references):
            scrapyed_info = {
                'model' : self.model,
                'bid' : self.bid_split(item[0].url),
                'title' : item[1],
                'link' : item[0].url,
                'date' : item[2].replace('.','-'),
                'author' : item[3],
                'reference' : item[4] if item[4] else None, # reference가 있다면 strip()
            }
            yield scrapyed_info

class MainSpider(DefaultSpider):
    name = 'main_spider'
    start_urls = ['https://www.kangwon.ac.kr/www/selectBbsNttList.do?bbsNo=37']
    def __init__(self):
        from crawling import models
        super().__init__()
        super().set_args(
            model = models.Main,
            bid = 'nttNo',
            url_xpath = '//*[@id="board"]/table/tbody/tr/td[3]/a',
            titles_xpath = '//*[@id="board"]/table/tbody/tr/td[3]/a/text()',
            dates_xpath = '//*[@id="board"]/table/tbody/tr/td[6]/text()',
            authors_xpath = '//*[@id="board"]/table/tbody/tr/td[4]/text()',
            references_xpath = '//*[@id="board"]/table/tbody/tr/td[2]/text()',
        )

class CseSpider(DefaultSpider):
    name = 'cse_spider'
    start_urls = ['https://cse.kangwon.ac.kr/index.php?mp=5_1_1']
    def __init__(self):
        from crawling import models
        super().__init__()
        super().set_args(
            model = models.Cse,
            bid = 'BID',
            url_xpath = '//*[@id="bbsWrap"]/table/tbody/tr/td[2]/a',
            titles_xpath = '//*[@id="bbsWrap"]/table/tbody/tr/td[2]/a/text()',
            dates_xpath = '//*[@id="bbsWrap"]/table/tbody/tr/td[4]/text()',
            authors_xpath = '//*[@id="bbsWrap"]/table/tbody/tr/td[3]/text()',
            references_xpath = None,
        )
