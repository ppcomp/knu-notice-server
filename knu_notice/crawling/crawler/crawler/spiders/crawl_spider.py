# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor

from crawling.data import data

'''
1. 각 class 구동시 필요한 import 구문은 class 안에 있어야 함.
 (scrapy에서 class만 갖고 crawling 하기 때문에 class 밖에 적어 놓으면 인식 불가.)
2. 비고(reference)가 없는 게시판이라면 xpath를 None으로 지정할 것.
3. set_args() 함수의 id 인자는 각 게시판에서 게시물을 구별할때 사용되는 키 값.
 (ex cse 게시판은 BID 사용, main 게시판은 nttNo 사용)
'''

class DefaultSpider(scrapy.Spider):

    # 객체 인스턴스에서 사용되는 변수 등록
    def set_args(self, args):
        self.model = args['model']
        self.id = args['id']
        self.url_xpath = args['url_xpath']
        self.titles_xpath = args['titles_xpath']
        self.dates_xpath = args['dates_xpath']
        self.authors_xpath = args['authors_xpath']
        self.references_xpath = args['references_xpath']

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

    # Link 객체에서 url과 id 추출
    # params: links
    # return: ids, urls
    def split_id_and_link(self, links):
        urls = []
        ids = []
        for link in links:
            urls.append(link.url+'&')
        for url in urls:
            idx = url.find(self.id)+len(self.id)+1
            for i in range(idx, len(url)):
                if url[i] == "&":
                    break
            ids.append(f'{self.name}-{url[idx:i]}')
        return ids, urls

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
        ids, links = self.split_id_and_link(links)      # id, link 추출
        dates = self.date_cleanse(dates)                # date 형식에 맞게 조정

        for item in zip(ids, titles, links, dates, authors, references):
            scrapyed_info = {
                'model' : self.model,
                'id' : item[0],
                'title' : item[1],
                'link' : item[2],
                'date' : item[3],
                'author' : item[4],
                'reference' : item[5],
            }
            yield scrapyed_info

'''
class MainSpider(DefaultSpider):
    def __init__(self):
        from crawling.data import data 
        args = data['main']
        self.name = args['name']
        self.start_urls = args['start_urls']
        super().__init__()
        super().set_args(args)
'''
# 위와 같은 형식의 Spider Class 자동 생성
for key, item in data.items():
    if key.find('test') == -1:
        txt = f"""
class {key.capitalize()}Spider(DefaultSpider):
    def __init__(self):
        from crawling.data import data 
        args = data['{key}']
        self.name = args['name']
        self.start_urls = args['start_urls']
        super().__init__()
        super().set_args(args)
"""
        exec(compile(txt,"<string>","exec"))
