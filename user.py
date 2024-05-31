import enum
import log
import telegram
import persistence

from typing import List


class AccountLevel(enum.Enum):
    User = 0
    Admin = 1


class User:
    chat_id = -1
    level = AccountLevel.User
    user: telegram.User

    def __init__(self, chat_id: int, level: AccountLevel, user: telegram.User):
        self.chat_id = chat_id
        self.level = level
        self.user = user
        log.logger.log("Новый пользователь создан: " + str(user.id) + ", " + str(level), log.MsgType.info, 'user')
        user_db.append(self)
        persistence.save(self)

    @staticmethod
    def user_registered(uid: int):
        for _user in user_db:
            if _user.user.id == uid:
                return True
        return False

    @staticmethod
    def get_admin():
        for current_user in user_db:
            if current_user.level == AccountLevel.Admin:
                return current_user

    @staticmethod
    def get_by_id(uid: int):
        for _user in user_db:
            if _user.user.id == uid:
                return _user

    @staticmethod
    def get_role(uid: int) -> AccountLevel:
        for _user in user_db:
            if _user.user.id == uid:
                return _user.level


user_db: List[User] = list()
MAX_USERS = 1000
