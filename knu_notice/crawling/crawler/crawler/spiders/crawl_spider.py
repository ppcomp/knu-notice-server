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

    # 객체 인스턴스에서 사용되는 변수 등록
    # params: model, bid, url_xpath, titles_xpath, dates_xpath, authores_xpath, references_xpath
    def set_args(self, model, bid, url_xpath, titles_xpath, dates_xpath, authors_xpath, references_xpath):
        self.model = model
        self.bid = bid
        self.url_xpath = url_xpath
        self.titles_xpath = titles_xpath
        self.dates_xpath = dates_xpath
        self.authors_xpath = authors_xpath
        self.references_xpath = references_xpath

    # 공백 제거. 가장 선행되어야 하는 전처리
    # params: items
    # return: ret
    def remove_whitespace(self, items):
        ret = []
        for item in items:
            x = item.strip()
            if x != '':
                ret.append(x)
        return ret

    # Link 객체에서 url과 bid 추출
    # params: links
    # return: bids, urls
    def split_bid_and_link(self, links):
        urls = []
        bids = []
        for link in links:
            urls.append(link.url+'&')
        for url in urls:
            idx = url.find(self.bid)+len(self.bid)+1
            for i in range(idx, len(url)):
                if url[i] == "&":
                    break
            bids.append(url[idx:i])
        return bids, urls

    # date 형식에 맞게 조정
    # ex 2020.05.19 > 2020-05-19
    # params: dates
    # return: dates
    def date_cleanse(self, dates):
        return [date.replace('.','-') for date in dates]

    def parse(self, response):
        url_forms = LinkExtractor(restrict_xpaths=self.url_xpath,attrs='href')
        links = url_forms.extract_links(response)
        titles = self.remove_whitespace(response.xpath(self.titles_xpath).extract())
        dates = self.remove_whitespace(response.xpath(self.dates_xpath).extract())
        authors = self.remove_whitespace(response.xpath(self.authors_xpath).extract())
        if self.references_xpath:
            references = self.remove_whitespace(response.xpath(self.references_xpath).extract())
        else:
            references = [None for _ in range(len(links))]

        # Data cleansing
        bids, links = self.split_bid_and_link(links)    # bid, link 추출
        dates = self.date_cleanse(dates)                # date 형식에 맞게 조정

        for item in zip(bids, titles, links, dates, authors, references):
            scrapyed_info = {
                'model' : self.model,
                'bid' : item[0],
                'title' : item[1],
                'link' : item[2],
                'date' : item[3],
                'author' : item[4],
                'reference' : item[5],
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
