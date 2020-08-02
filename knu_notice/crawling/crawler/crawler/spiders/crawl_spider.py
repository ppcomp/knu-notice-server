# -*- coding: utf-8 -*-
from typing import Dict, List, Tuple
import datetime
import re
import zlib

import scrapy
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
    def _data_verification(self, item: Dict[str, List]):
        from crawling import models
        when = f'While crawling {self.name}'
        title_len = len(item['titles'])

        # model check
        eval(f"models.{item['model']}")
        if title_len == 0:
            # empty check. 크롤링은 시도했으나 아무 데이터를 가져오지 못한 경우.
            raise Exception(f'{when}, Crawled item is empty! Check the xpaths or base url.')
        for key, value in item.items():
            if key in ('id','link'):
                if len(value) != title_len:
                    # size check. 크롤링된 데이터들이 길이가 다른 경우
                    raise Exception(f"{when}, {key} size is not same with title's. ({key} size: {len(value)}, id size: {title_len})")
            if ((key == 'dates' and self.dates_xpath) or
                (key == 'authors' and self.authors_xpath) or
                (key == 'references' and self.references_xpath)):
                # valid check. 크롤링된 데이터의 유효성 검증.
                if value[0] is None:
                    raise Exception(f'{when}, {key} is None.')
                if value[0] == '':
                    raise Exception(f'{when}, {key} is empty. ("")')

    # 객체 인스턴스에서 사용되는 변수 등록
    def set_args(self, args: Dict):
        self.model = args['model']
        self.id = args['id']
        self.is_fixed = args['is_fixed']
        self.url_xpath = args['url_xpath']
        self.titles_xpath = args['titles_xpath']
        self.dates_xpath = args['dates_xpath']
        self.authors_xpath = args['authors_xpath']
        self.references_xpath = args['references_xpath']

    # 공백 제거. 가장 선행되어야 하는 전처리
    def remove_whitespace(self, items: List[str]) -> List[str]:
        ret = []
        for item in items:
            x = item.strip()
            if x != '':
                ret.append(x)
        return ret

    # Link 객체에서 url과 id 추출
    def split_id_and_link(self, links: List[str]) -> Tuple[List[str],List[str]]:
        urls = []
        ids = []
        for link in links:
            urls.append(link.url+'&')
        for url in urls:
            idx = url.find(self.id)+len(self.id)+1
            for i in range(idx, len(url)):
                if url[i] == "&":
                    break
            id = url[idx:i]
            if len(id) > 20:
                seed = id.encode('utf-8')
                id = zlib.adler32(seed)
            ids.append(f'{self.name}-{id}')
        return ids, urls

    # date 형식에 맞게 조정
    def date_cleanse(self, dates: List[str]) -> List[str]:
        today = datetime.date.today()
        today_format = today.strftime("%Y-%m-%d")
        type1 = re.compile(r'^\d{2}-\d{2}$')        # 05-19
        type2 = re.compile(r'^\d{2}-\d{2}-\d{2}$')  # 20-05-19
        type3 = re.compile(r'^\d{4}-\d{2}-\d{2}$')  # 2020-05-19

        fix1 = []
        for date in dates:
            d = date.replace('.','-')               # 2020.05.19 > 2020-05-19
            d = d.replace('/','-')                  # 11:35 > 2020-05-19
            fix1.append(d)

        fix2 = []
        for d in fix1:
            if d.find(':') != -1:
                fix2.append(today_format)
            elif type1.match(d):                                    # 05-19
                try:
                    tmp = datetime.datetime.strptime(d, "%m-%d")    # datetime 객체로 변환 (1900-05-19)
                    tmp = tmp.replace(year=today.year)              # datetime 객체 년도 수정 (2020-05-19)
                    tmp = tmp.strftime("%Y-%m-%d")                  # string으로 변환 (2020-05-19)
                except:
                    tmp = None
                fix2.append(tmp)
            elif type2.match(d):                                    # 20-05-19
                try:
                    tmp = datetime.datetime.strptime(d, "%y-%m-%d") # datetime 객체로 변환 (2020-05-19)
                    tmp = tmp.strftime("%Y-%m-%d")                  # string으로 변환 (2020-05-19)
                except:
                    tmp = None
                fix2.append(tmp)
            elif type3.match(d):                                    # 2020-05-19
                try:
                    tmp = datetime.datetime.strptime(d, "%Y-%m-%d")
                    tmp = tmp.strftime("%Y-%m-%d")
                except:
                    tmp = None
                fix2.append(tmp)

        return fix2

    def extend_list(self, arr:List[str], target:int) -> List[str]:
        add = [None for i in range(target)]
        return arr + add

    # Override parse()
    def parse(self, response) -> Dict:
        if response.status == 404:
            raise Exception('404 Page not foud! Check the base url.')

        url_forms = MyLinkExtractor(restrict_xpaths=self.url_xpath, attrs='href')
        
        links: List[str] = url_forms.extract_links(response, omit=False)

        titles: List[str] = self.remove_whitespace(
            response.xpath(self.titles_xpath).getall())

        if self.is_fixed:
            is_fixeds: List[str] = self.remove_whitespace(
                response.xpath(self.is_fixed).getall())
        else:
            is_fixeds: List[None] = [None for _ in range(len(links))]

        if self.dates_xpath:
            dates: List[str] = self.remove_whitespace(
                response.xpath(self.dates_xpath).getall())
            dates = self.date_cleanse(dates)        # date 형식에 맞게 조정
        else:
            dates: List[None] = [None for _ in range(len(links))]

        if self.authors_xpath:
            authors: List[str] = self.remove_whitespace(
                response.xpath(self.authors_xpath).getall())
        else:
            authors: List[None] = [None for _ in range(len(links))]

        if self.references_xpath:
            references: List[str] = self.remove_whitespace(
                response.xpath(self.references_xpath).getall())
        else:
            references: List[None] = [None for _ in range(len(links))]

        ids, links = self.split_id_and_link(links)  # id, link 추출
        is_fixeds = self.extend_list(is_fixeds, len(ids)-len(is_fixeds))

        self._data_verification({
            'model':self.model,
            'ids':ids, 
            'is_fixeds':is_fixeds,
            'titles':titles, 
            'links':links, 
            'dates':dates, 
            'authors':authors, 
            'references':references,
        })

        for id, is_fixed, title, link, date, author, reference in zip(
            ids, is_fixeds, titles, links, dates, authors, references):
            scrapyed_info = {
                'model' : self.model,
                'id' : id,
                'site' : self.model.lower(),
                'is_fixed' : is_fixed,
                'title' : title,
                'link' : link,
                'date' : date,
                'author' : author,
                'reference' : reference,
            }
            yield scrapyed_info

page_num = 1
# Spider Class 자동 생성
for key, item in data.items():
    if key.find('test') == -1:
        txt = f"""
class {key.capitalize()}Spider(DefaultSpider):
    def __init__(self):
        from crawling.data import data
        args = data['{key}']

        self.name = args['name']
        if args['page']:
            url:str = args['start_urls']
            url_page = url + '&' + args['page'] + '=%d'
            urls = [url_page % i for i in range(1, page_num+1)]
            self.start_urls = urls
        else:
            self.start_urls = [args['start_urls']]

        super().__init__()
        super().set_args(args)
"""
        exec(compile(txt,"<string>","exec"))
