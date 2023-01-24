# -*- coding: utf-8 -*-
from typing import Dict, List, Tuple
import datetime
from urllib.parse import urljoin
import logging
from logging.config import dictConfig
import re
import zlib

from django.conf import settings
import scrapy
from scrapy.downloadermiddlewares.retry import get_retry_request
from scrapy.http import Response
from scrapy.http.request import Request
from scrapy.utils.response import get_base_url
from crawling.data import data

'''
1. 각 class 구동시 필요한 import 구문은 class 안에 있어야 함.
 (scrapy에서 class만 갖고 crawling 하기 때문에 class 밖에 적어 놓으면 인식 불가.)
2. 비고(reference)가 없는 게시판이라면 xpath를 None으로 지정할 것.
3. set_args() 함수의 bid 인자는 각 게시판에서 게시물을 구별할때 사용되는 키 값.
 (ex cse 게시판은 BID 사용, main 게시판은 nttNo 사용)
'''


class DefaultSpider(scrapy.Spider):
    handle_httpstatus_list = [404]

    # 데이터 검증
    def _data_verification(self, response, item: Dict[str, List]):
        when = f'While crawling {self.name}'
        link_len = len(item['links'])

        # model check
        from crawling import models
        eval(f"models.{item['model']}")
        if link_len == 0:
            # empty check. 크롤링은 시도했으나 아무 데이터를 가져오지 못한 경우.
            return False
        for key, value in item.items():
            if key not in ('model'):
                if len(value) != link_len:
                    # size check. 크롤링된 데이터들이 길이가 다른 경우
                    raise Exception(
                        f"{when}, {key} size is not same with link's. ({key} size: {len(value)}, link size: {link_len})")
            # if ((key == 'dates' and self.date_xpath) or
            #     (key == 'authors' and self.author_xpath) or
            #     (key == 'references' and self.reference_xpath)):
            #     # valid check. 크롤링된 데이터의 유효성 검증.
            #     if value[0] == '':
            #         raise Exception(f'{when}, {key} is empty. ("")')
        return True

    # 객체 인스턴스에서 사용되는 변수 등록
    def set_args(self, args: Dict):
        self.model = args['model']
        self.bid_param = args['bid_param']
        self.url_xpath = args['url_xpath']
        title_xpath = args['title_xpath']
        fixed_xpath = args['fixed_xpath']
        date_xpath = args['date_xpath']
        author_xpath = args['author_xpath']
        reference_xpath = args['reference_xpath']
        self.inside_date_xpath = args['inside_date_xpath']
        self.drop_offset = args['drop_offset']

        tag = 'tr/'
        row_idx = self.url_xpath.rfind(tag)
        if row_idx == -1:
            tag = 'li/'
            row_idx = self.url_xpath.rfind(tag)
        self.child_url_xpath = './' + self.url_xpath[self.url_xpath.rfind(tag) + 3:]
        self.row_xpath = self.url_xpath[:row_idx + 2]
        self.title_xpath = './' + title_xpath[title_xpath.rfind(tag) + 3:]
        self.fixed_xpath = './' + fixed_xpath[fixed_xpath.rfind(tag) + 3:] if fixed_xpath else None
        self.date_xpath = './' + date_xpath[date_xpath.rfind(tag) + 3:] if date_xpath else None
        self.author_xpath = './' + author_xpath[author_xpath.rfind(tag) + 3:] if author_xpath else None
        self.reference_xpath = './' + reference_xpath[reference_xpath.rfind(tag) + 3:] if reference_xpath else None

    # 공백 제거. 가장 선행되어야 하는 전처리
    # How about use strip_html5_whitespace?
    # https://w3lib.readthedocs.io/en/latest/w3lib.html#w3lib.html.strip_html5_whitespace
    def remove_whitespace(self, items: List[str]) -> List[str]:
        ret = []
        for item in items:
            x = item
            if x:
                x = item.strip()
                x = x.replace('<', '＜').replace('>', '＞')  # ㄷ 한자(특수문자)
            ret.append(x)
        return ret

    # Link 객체에서 url과 bid 추출
    def split_id_and_link(self, links: List[str]) -> Tuple[List[str], List[str]]:
        bids = []
        urls = []
        for link in links:
            urls.append(link + '&')
        for url in urls:
            if self.bid_param == 'restful':
                idx = url.rfind('/') + 1
                if url[idx] == '?':
                    idx = url[:idx - 1].rfind('/') + 1
            else:
                idx = url.rfind(self.bid_param + '=') + len(self.bid_param) + 1
            for i in range(idx, len(url)):
                if url[i] in ('&', '?'):
                    break
            bid = url[idx:i]
            if len(bid) > 20:
                seed = bid.encode('utf-8')
                bid = zlib.adler32(seed)
            bids.append(f'{self.name}-{bid}')
        return bids, links

    # date 형식에 맞게 조정
    def date_cleanse(self, dates: List[str]) -> List[str]:
        today = datetime.date.today()
        today_format = today.strftime("%Y-%m-%d")
        type1 = re.compile(r'\d{4}-\d{2}-\d{2}')  # 2020-05-19
        type2 = re.compile(r'\d{2}-\d{2}-\d{2}')  # 20-05-19

        fix1 = []
        for date in dates:
            if date:
                d = date.replace('.', '-')  # 2020.05.19 > 2020-05-19
                d = d.replace('/', '-')  # 2020/05/19 > 2020-05-19
                d = d.replace('·', '-')  # 2020·05·19 > 2020-05-19
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
            if type1s:  # 2020-05-19
                try:
                    tmp = datetime.datetime.strptime(type1s[0], "%Y-%m-%d")
                    tmp = tmp.strftime("%Y-%m-%d")
                except:
                    tmp = None
            elif type2s:  # 20-05-19
                try:
                    tmp = datetime.datetime.strptime(type2s[0], "%y-%m-%d")  # datetime 객체로 변환 (2020-05-19)
                    tmp = tmp.strftime("%Y-%m-%d")  # string으로 변환 (2020-05-19)
                except:
                    tmp = None
            elif d.find(':') != -1:
                tmp = today_format
            fix2.append(tmp)

        return fix2

    def parse_inside(self, response):
        s_list = response.xpath(self.inside_date_xpath).getall()
        s = ' '.join([t.strip() for t in s_list if t.strip() != ''])
        scraped_info = response.meta['scraped_info']
        scraped_info['date'] = self.date_cleanse([s])[0]
        self.scraped_info_data.append(scraped_info)

    def extend_list(self, arr: List[str], target: int) -> List[str]:
        add = [None for _ in range(target)]
        return arr + add

    # Override
    def parse(self, response: Response):
        if response.status == 404:
            raise Exception('404 Page not foud! Check the base url.')

        response = self._preprocess_response(response)

        authors, dates, is_fixeds, links, references, titles = self._parse_outside(response)

        bids, links = self.split_id_and_link(links)  # bid, link 추출
        titles = self.remove_whitespace(titles)
        is_fixeds = self.remove_whitespace(is_fixeds)
        dates = self.remove_whitespace(dates)
        authors = self.remove_whitespace(authors)
        references = self.remove_whitespace(references)

        dates = self.date_cleanse(dates)  # date 형식에 맞게 조정
        is_fixeds = self.extend_list(is_fixeds, len(bids) - len(is_fixeds))
        if not self._data_verification(response, {
            'model': self.model,
            'ids': bids,
            'is_fixeds': is_fixeds,
            'titles': titles,
            'links': links,
            'dates': dates,
            'authors': authors,
            'references': references,
        }):
            return get_retry_request(
                response.request,
                max_retry_times=3,
                spider=self,
            )

        for bid, is_fixed, title, link, date, author, reference in zip(
                bids, is_fixeds, titles, links, dates, authors, references):
            scraped_info = {
                'id': bid,
                'site': self.model.lower(),
                'is_fixed': is_fixed,
                'title': title,
                'link': link,
                'date': date,
                'author': author,
                'reference': reference,
            }
            if not date and self.inside_date_xpath:
                request = Request(link, callback=self.parse_inside)
                request.meta['scraped_info'] = scraped_info
                yield request
            else:
                self.scraped_info_data.append(scraped_info)
            # yield scraped_info
        # print(f"Success! {self.name}")

    def _parse_outside(self, response: Response):
        base_url = get_base_url(response)
        row_datas = response.xpath(self.row_xpath)
        links = []
        titles = []
        is_fixeds = []
        dates = []
        authors = []
        references = []
        for row in row_datas[self.drop_offset:]:
            child_url = row.xpath(self.child_url_xpath + '/@href')
            if child_url:
                links.append(self._build_link(base_url, child_url))
                try:
                    s_list = row.xpath(self.title_xpath).getall()
                    s = ' '.join([t.strip() for t in s_list if t.strip() != ''])
                    titles.append(s if s else '')
                except:
                    titles.append('')
                try:
                    s_list = row.xpath(self.fixed_xpath).getall()
                    s = ' '.join([t.strip() for t in s_list if t.strip() != ''])
                    is_fixeds.append(s if s else False)
                except:
                    is_fixeds.append(False)
                try:
                    s_list = row.xpath(self.date_xpath).getall()
                    s = ' '.join([t.strip() for t in s_list if t.strip() != ''])
                    dates.append(s)
                except:
                    dates.append(None)
                try:
                    s_list = row.xpath(self.author_xpath).getall()
                    s = ' '.join([t.strip() for t in s_list if t.strip() != ''])
                    authors.append(s)
                except:
                    authors.append(None)
                try:
                    s_list = row.xpath(self.reference_xpath).getall()
                    s = ' '.join([t.strip() for t in s_list if t.strip() != ''])
                    references.append(s)
                except:
                    references.append(None)
        return authors, dates, is_fixeds, links, references, titles

    def _build_link(self, base_url, child_url):
        return urljoin(base_url, child_url.get())

    def _preprocess_response(self, response):
        return response

    # Override
    def close(self, spider, reason):
        # for info in self.scraped_info_data:
        #     print(f"Success! {self.name} {info['date']} {info['title']}")
        self.output_callback(self.scraped_info_data)


page_num = 1
manual_spiders = {
    'knudorm'
}
# Spider Class 자동 생성
for key, item in data.items():
    if 'test' not in key and key not in manual_spiders:
        txt = f"""
class {key.capitalize()}Spider(DefaultSpider):
    def __init__(self, **kwargs):
        from logging.config import dictConfig
        from django.conf import settings
        dictConfig(settings.LOGGING)
        logger = logging.getLogger('scrapy')

        from crawling.data import data
        args = data['{key}']

        self.name = args['name']
        if args['page_param']:
            url:str = args['start_url']
            if args['page_param'] == 'restful':
                url_page = url + '/' + '%d'
            elif args['page_param'] == 'offset':
                url_page = url
            else:
                url_page = url + '&' + args['page_param'] + '=%d'
            if args['page_param'] == 'offset':
                urls = [url_page % ((i-1)*20) for i in range(1, page_num+1)]
            else:
                urls = [url_page % i for i in range(1, page_num+1)]
            self.start_urls = urls
        else:
            self.start_urls = [args['start_url']]

        self.output_callback = kwargs.get('args').get('callback')
        self.scraped_info_data = []
        super().__init__(**kwargs)
        super().set_args(args)
    
"""
        exec(compile(txt, "<string>", "exec"))


class KnudormSpider(DefaultSpider):
    def __init__(self, **kwargs):
        dictConfig(settings.LOGGING)
        logger = logging.getLogger('scrapy')
        args = data['knudorm']
        self.name = args['name']
        self.start_urls = [args['start_url'] for _ in range(page_num)]
        self.output_callback = kwargs.get('args').get('callback')
        self.scraped_info_data = []
        super().__init__(**kwargs)
        super().set_args(args)

    # Override
    def start_requests(self):
        if not self.start_urls and hasattr(self, 'start_url'):
            raise AttributeError(
                "Crawling could not start: 'start_urls' not found "
                "or empty (but found 'start_url' attribute instead, "
                "did you miss an 's'?)")
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
        }
        for i in range(1, page_num + 1):
            body = 'boardId=4&userListRowCnt=10&pagedListSearchCondition={"pageSize":"10","currentPage":"%s","pageLimit":"10","searchKeys":["subject","summary","user_name"],"method":"S","searchInResult":"N","searchParams":[{"key":"subject","column":"SUBJECT","type":"string","operator":"like"},{"key":"summary","column":"CONTENT_SUMMARY","type":"string","operator":"like"},{"key":"user_name","column":"A.USER_NAME","type":"string","operator":"like"},{"key":"nick_name","column":"NICK_NAME","type":"string","operator":"like"},{"key":"write_date","column":"WRITE_DATE","type":"date","operator":"between"},{"key":"branchName","column":"BRANCH_NAME","type":"string","operator":"like"},{"key":"apprStatus","column":"APP_STATUS","type":"string","operator":"eq"},{"key":"user_dept_name","column":"USER_DEPT_NAME","type":"string","operator":"like"}],"orders":[{"field":"ARTICLE_SEQ+DESC,+ORDER_GROUP","order":""}],"link":"goPage","headerSortYn":"N","headerSortField":"","headerSortOrderBy":"","scrollPaging":"N","startOffset":"0","endOffset":"0"}' \
                   % i
            yield Request(self.start_urls[0], method='POST', headers=headers, body=body)

    # Override
    def _build_link(self, base_url, child_url):
        return 'https://knudorm.kangwon.ac.kr/dorm/bbs/bbsView.knu?newPopup=true&boardMode=COMPANY&articleId=' + child_url.get().split('\'')[1]

    # Override
    def _preprocess_response(self, response: Response):
        text = response.text
        text = text.replace('<![CDATA[', '')
        text = text.replace(']]>', '')
        response = response.replace(body=bytes(text, 'utf-8'))

        return response
