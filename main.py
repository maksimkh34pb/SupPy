import asyncio
import os

import telegram

from dotenv import load_dotenv


async def main():
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)

    bot = telegram.Bot(os.environ.get('BOT_TOKEN'))
    async with bot:
        print(await bot.get_me())


if __name__ == '__main__':
    asyncio.run(main())
