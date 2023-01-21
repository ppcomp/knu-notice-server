from support import models

board_infos = models.BoardInfo.objects.all()
data = dict()
for board_info in board_infos:
    data[board_info.code] = dict(board_info.__dict__)
