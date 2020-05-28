from crawling import models

data = {
    'main' : {
        'api_url' : '/notice/main/',
        'name' : '강원대학교',
        'start_urls' : ['https://www.kangwon.ac.kr/www/selectBbsNttList.do?bbsNo=37'],
        'model' : models.Main,
        'id' : 'nttNo',
        'url_xpath' : '//*[@id="board"]/table/tbody/tr/td[3]/a',
        'titles_xpath' : '//*[@id="board"]/table/tbody/tr/td[3]/a/text()',
        'dates_xpath' : '//*[@id="board"]/table/tbody/tr/td[6]/text()',
        'authors_xpath' : '//*[@id="board"]/table/tbody/tr/td[4]/text()',
        'references_xpath' : '//*[@id="board"]/table/tbody/tr/td[2]/text()',
    },
    'cse' : {
        'api_url' : '/notice/cse/',
        'name' : '컴퓨터공학과',
        'start_urls' : ['https://cse.kangwon.ac.kr/index.php?mp=5_1_1'],
        'model' : models.Cse,
        'id' : 'BID',
        'url_xpath' : '//*[@id="bbsWrap"]/table/tbody/tr/td[2]/a',
        'titles_xpath' : '//*[@id="bbsWrap"]/table/tbody/tr/td[2]/a/text()',
        'dates_xpath' : '//*[@id="bbsWrap"]/table/tbody/tr/td[4]/text()',

        'authors_xpath' : '//*[@id="bbsWrap"]/table/tbody/tr/td[3]/text()',
        'references_xpath' : None,
    },
    'testboard1' : {
        'api_url' : '/notice/testboard1',
        'name' : '테스트학과1',
    },
    'testboard2' : {
        'api_url' : '/notice/testboard2',
        'name' : '테스트학과2',
    },
    'testboard3' : {
        'api_url' : '/notice/testboard3',
        'name' : '테스트학과3',
    },
    'testboard4' : {
        'api_url' : '/notice/testboard4',
        'name' : '테스트학과4',
    },
    'testboard5' : {
        'api_url' : '/notice/testboard5',
        'name' : '테스트학과5',
    },
    'testboard6' : {
        'api_url' : '/notice/testboard6',
        'name' : '테스트학과6',
    },
    'testboard7' : {
        'api_url' : '/notice/testboard7',
        'name' : '테스트학과7',
    },
    'testboard8' : {
        'api_url' : '/notice/testboard8',
        'name' : '테스트학과8',
    },
}