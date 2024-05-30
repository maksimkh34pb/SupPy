import os
import bot
import log
from dotenv import load_dotenv

import persistence
import user


def main():
    # Load env vars

    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)

    # load users

    user.user_db = persistence.load()
    log.logger.log('Всего пользователей загружено: ' + str(len(user.user_db)), log.MsgType.info, 'main')

    # init bot

    bot.init(os.environ.get("BOT_TOKEN"))
    log.logger.destructor()  # destroy logger after bot polling


if __name__ == '__main__':
    main()
