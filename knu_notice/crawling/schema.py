from drf_yasg.openapi import Schema


BOARD_SCHEMA = Schema(
    title='Board', type='object',
    properties={
        'code': Schema(type='string'),
        'keywords': Schema(description='구분자: +', type='string'),
    }
)


PUSH_SCHEMA = Schema(
    title='Push', type='object',
    properties={
        'broad_cast': Schema(description='알람 킨 디바이스에 대해 모두 push. 1순위', type='boolean', default=False),
        'all': Schema(description='모든 게시판에 글이 올라온 상황을 가정하고 push. 2순위', type='boolean', default=False),
        'targets': Schema(description='특정 게시판 및 키워드가 올라온 상황을 가정하고 push', type='array', items=BOARD_SCHEMA),
        'device_ids': Schema(description='푸시 알림을 보낼 디바이스 id. 구분자: +', type='string', default=''),
    }
)


class Board:
    def __init__(self, code, keywords):
        self.code: str = code
        self.keywords: str = keywords


class Push:
    def __init__(self, broad_cast, all, targets, device_ids):
        self.broad_cast: bool = broad_cast
        self.all: bool = all
        self.targets: list[Board] = [Board(**j) for j in targets]
        self.device_ids: list[str] = device_ids.split('+')
