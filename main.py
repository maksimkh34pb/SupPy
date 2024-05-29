import os
from dotenv import load_dotenv

import bot
import log


def main():
    # Load env vars

    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)

    # init bot

    bot.init(os.environ.get("BOT_TOKEN"))
    log.logger.destructor()     # destroy logger after bot polling


if __name__ == '__main__':
    main()
