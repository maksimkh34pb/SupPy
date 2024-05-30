import enum
import log

from typing import List

import persistence


class AccountLevel(enum.Enum):
    User = 0
    Admin = 1


class User:
    tg_id = -1
    chat_id = -1
    level = AccountLevel.User

    def __init__(self, tg_id: int, chat_id: int, level: AccountLevel):
        self.tg_id = tg_id
        self.chat_id = chat_id
        self.level = level
        log.logger.log("Новый пользователь создан: " + str(tg_id) + ", " + str(level.value), log.MsgType.info, 'user')
        user_db.append(self)
        persistence.save(self)

    @staticmethod
    def user_registered(uid: int):
        for user in user_db:
            if user.tg_id == uid:
                return True
        return False


user_db: List[User] = list()
MAX_USERS = 1000
