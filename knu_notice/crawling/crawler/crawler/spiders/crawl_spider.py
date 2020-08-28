# -*- coding: utf-8 -*-
from typing import Dict, List, Tuple
import datetime
from urllib.parse import urljoin
import re
import requests
import zlib

from bs4 import BeautifulSoup
import scrapy
from scrapy.http.request import Request
from scrapy.linkextractors import LinkExtractor
from scrapy.utils.response import get_base_url
from scrapy_splash import SplashRequest
from crawling.data import data
from .LinkExtractor import MyLinkExtractor

'''
1. 각 class 구동시 필요한 import 구문은 class 안에 있어야 함.
 (scrapy에서 class만 갖고 crawling 하기 때문에 class 밖에 적어 놓으면 인식 불가.)
2. 비고(reference)가 없는 게시판이라면 xpath를 None으로 지정할 것.
3. set_args() 함수의 id 인자는 각 게시판에서 게시물을 구별할때 사용되는 키 값.
 (ex cse 게시판은 BID 사용, main 게시판은 nttNo 사용)
'''

class DefaultSpider(scrapy.Spider):

    handle_httpstatus_list = [404]

    # 데이터 검증
    def _data_verification(self, response, item: Dict[str, List]):
        from crawling import models
        when = f'While crawling {self.name}'
        link_len = len(item['links'])

        # model check
        eval(f"models.{item['model']}")
        if link_len == 0:
            # empty check. 크롤링은 시도했으나 아무 데이터를 가져오지 못한 경우.
            if self.try_time < 5:
                return False
            else:
                raise Exception(f'{when}, Crawled item is empty! Xpaths and base url is wrong or connection has failed.')
        for key, value in item.items():
            if key not in ('model'):
                if len(value) != link_len:
                    # size check. 크롤링된 데이터들이 길이가 다른 경우
                    raise Exception(f"{when}, {key} size is not same with link's. ({key} size: {len(value)}, link size: {link_len})")
            # if ((key == 'dates' and self.dates_xpath) or
            #     (key == 'authors' and self.authors_xpath) or
            #     (key == 'references' and self.references_xpath)):
            #     # valid check. 크롤링된 데이터의 유효성 검증.
            #     if value[0] == '':
            #         raise Exception(f'{when}, {key} is empty. ("")')
        return True

    # 객체 인스턴스에서 사용되는 변수 등록
    def set_args(self, args: Dict):
        self.model = args['model']
        self.id = args['id']
        self.url_xpath = args['url_xpath']
        titles_xpath = args['titles_xpath']
        is_fixed = args['is_fixed']
        dates_xpath = args['dates_xpath']
        authors_xpath = args['authors_xpath']
        references_xpath = args['references_xpath']
        self.in_date_xpath = args['in_date_xpath']
        self.drop = args['drop']

        tag = 'tr/'
        row_idx = self.url_xpath.rfind(tag)
        if row_idx == -1:
            tag = 'li/'
            row_idx = self.url_xpath.rfind(tag)
        self.child_url_xpath = './'+self.url_xpath[self.url_xpath.rfind(tag)+3:]
        self.row_xpath = self.url_xpath[:row_idx+2]
        self.titles_xpath = './'+titles_xpath[titles_xpath.rfind(tag)+3:]
        self.is_fixed = './'+is_fixed[is_fixed.rfind(tag)+3:] if is_fixed else None
        self.dates_xpath = './'+dates_xpath[dates_xpath.rfind(tag)+3:] if dates_xpath else None
        self.authors_xpath = './'+authors_xpath[authors_xpath.rfind(tag)+3:] if authors_xpath else None
        self.references_xpath = './'+references_xpath[references_xpath.rfind(tag)+3:] if references_xpath else None

    # 공백 제거. 가장 선행되어야 하는 전처리
    # How about use strip_html5_whitespace?
    # https://w3lib.readthedocs.io/en/latest/w3lib.html#w3lib.html.strip_html5_whitespace
    def remove_whitespace(self, items: List[str]) -> List[str]:
        ret = []
        for item in items:
            x = item
            if x:
                x = item.strip()
                x = x.replace('<', '＜').replace('>', '＞') # ㄷ 한자(특수문자)
            ret.append(x)
        return ret

    # Link 객체에서 url과 id 추출
    def split_id_and_link(self, links: List[str]) -> Tuple[List[str],List[str]]:
        ids = []
        urls = []
        for link in links:
            urls.append(link+'&')
        for url in urls:
            if self.id == 'restful':
                idx = url.rfind('/')+1
            else:
                idx = url.rfind(self.id+'=')+len(self.id)+1
            for i in range(idx, len(url)):
                if url[i] in ('&','?'):
                    break
            id = url[idx:i]
            if len(id) > 20:
                seed = id.encode('utf-8')
                id = zlib.adler32(seed)
            ids.append(f'{self.name}-{id}')
        return ids, links

    # date 형식에 맞게 조정
    def date_cleanse(self, dates: List[str]) -> List[str]:
        today = datetime.date.today()
        today_format = today.strftime("%Y-%m-%d")
        type1 = re.compile(r'\d{4}-\d{2}-\d{2}')  # 2020-05-19
        type2 = re.compile(r'\d{2}-\d{2}-\d{2}')  # 20-05-19

        fix1 = []
        for date in dates:
            if date:
                d = date.replace('.','-')               # 2020.05.19 > 2020-05-19
                d = d.replace('/','-')                  # 2020/05/19 > 2020-05-19
                d = d.replace('·','-')                  # 2020·05·19 > 2020-05-19
                fix1.append(d)
            else:
                fix1.append(date)

        fix2 = []
        for d in fix1:
            if not d:
                fix2.append(None)
                continue
            type1s = type1.findall(d)
            type2s = type2.findall(d)
            tmp = None
            if type1s:                                              # 2020-05-19
                try:
                    tmp = datetime.datetime.strptime(type1s[0], "%Y-%m-%d")
                    tmp = tmp.strftime("%Y-%m-%d")
                except:
                    tmp = None
            elif type2s:                                            # 20-05-19
                try:
                    tmp = datetime.datetime.strptime(type2s[0], "%y-%m-%d") # datetime 객체로 변환 (2020-05-19)
                    tmp = tmp.strftime("%Y-%m-%d")                  # string으로 변환 (2020-05-19)
                except:
                    tmp = None
            elif d.find(':') != -1:
                tmp = today_format
            fix2.append(tmp)

        return fix2

    def parse_inside(self, response):
        s_list = response.xpath(self.in_date_xpath).getall()
        s = ' '.join([t.strip() for t in s_list if t.strip() != ''])
        scraped_info = response.meta['scraped_info']
        scraped_info['date'] = self.date_cleanse([s])[0]
        self.scraped_info_data.append(scraped_info)

    def extend_list(self, arr:List[str], target:int) -> List[str]:
        add = [None for i in range(target)]
        return arr + add

    # Override
    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url, self.parse,
                endpoint='render.html',
                args={'wait': 0.5},
            )

    # Override
    def parse(self, response):
        if response.status == 404:
            raise Exception('404 Page not foud! Check the base url.')

        base_url = get_base_url(response)
        row_datas = response.xpath(self.row_xpath)
        links = []
        titles = []
        is_fixeds = []
        dates = []
        authors = []
        references = []

        for row in row_datas[self.drop:]:
            child_url = row.xpath(self.child_url_xpath+'/@href')
            if child_url:
                links.append(urljoin(base_url, child_url.get()))
                try:
                    s_list = row.xpath(self.titles_xpath).getall()
                    s = ' '.join([t.strip() for t in s_list if t.strip() != ''])
                    titles.append(s if s else '')
                except:
                    titles.append('')
                try:
                    s_list = row.xpath(self.is_fixed).getall()
                    s = ' '.join([t.strip() for t in s_list if t.strip() != ''])
                    is_fixeds.append(s if s else False)
                except:
                    is_fixeds.append(False)
                try:
                    s_list = row.xpath(self.dates_xpath).getall()
                    s = ' '.join([t.strip() for t in s_list if t.strip() != ''])
                    dates.append(s)
                except:
                    dates.append(None)
                try:
                    s_list = row.xpath(self.authors_xpath).getall()
                    s = ' '.join([t.strip() for t in s_list if t.strip() != ''])
                    authors.append(s)
                except:
                    authors.append(None)
                try:
                    s_list = row.xpath(self.references_xpath).getall()
                    s = ' '.join([t.strip() for t in s_list if t.strip() != ''])
                    references.append(s)
                except:
                    references.append(None)

        ids, links = self.split_id_and_link(links)  # id, link 추출
        titles = self.remove_whitespace(titles)
        is_fixeds = self.remove_whitespace(is_fixeds)
        dates = self.remove_whitespace(dates)
        authors = self.remove_whitespace(authors)
        references = self.remove_whitespace(references)

        dates = self.date_cleanse(dates)        # date 형식에 맞게 조정
        is_fixeds = self.extend_list(is_fixeds, len(ids)-len(is_fixeds))
        if self._data_verification(response, {
            'model':self.model,
            'ids':ids, 
            'is_fixeds':is_fixeds,
            'titles':titles, 
            'links':links, 
            'dates':dates, 
            'authors':authors, 
            'references':references,
        }):
            self.try_time = 0
        else:
            self.try_time += 1
            yield SplashRequest(response.url, callback=self.parse, dont_filter=True)
            return

        for id, is_fixed, title, link, date, author, reference in zip(
            ids, is_fixeds, titles, links, dates, authors, references):
            scraped_info = {
                'id' : id,
                'site' : self.model.lower(),
                'is_fixed' : is_fixed,
                'title' : title,
                'link' : link,
                'date' : date,
                'author' : author,
                'reference' : reference,
            }
            if not date and self.in_date_xpath:
                request = SplashRequest(link, callback=self.parse_inside,
                    endpoint='render.html',
                    args={'wait': 0.5},
                )
                request.meta['scraped_info'] = scraped_info
                yield request
            else:
                self.scraped_info_data.append(scraped_info)
            # yield scraped_info
        # print(f"Success! {self.name}")

    # Override
    def close(self, spider, reason):
        # for info in self.scraped_info_data:
        #     print(f"Success! {self.name} {info['date']} {info['title']}")
        self.output_callback(self.scraped_info_data)

page_num = 1
# Spider Class 자동 생성
for key, item in data.items():
    if key.find('test') == -1:
        txt = f"""
class {key.capitalize()}Spider(DefaultSpider):
    def __init__(self, **kwargs):
        from crawling.data import data
        args = data['{key}']
        self.try_time = 0

        self.name = args['name']
        if args['page']:
            url:str = args['start_urls']
            if args['page'] == 'restful':
                url_page = url + '/' + '%d'
            else:
                url_page = url + '&' + args['page'] + '=%d'
            urls = [url_page % i for i in range(1, page_num+1)]
            self.start_urls = urls
        else:
            self.start_urls = [args['start_urls']]

        self.output_callback = kwargs.get('args').get('callback')
        self.scraped_info_data = []
        super().__init__(**kwargs)
        super().set_args(args)
"""
        exec(compile(txt,"<string>","exec"))
