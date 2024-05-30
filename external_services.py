import bot
import log
import user


async def send_to_support(text: str):
    log.logger.log('New support msg: ' + text, log.MsgType.info, 'external services')
    for current_user in user.user_db:
        if current_user.level == user.AccountLevel.Admin:
            await bot.global_bot.send_message(chat_id=current_user.chat_id,
                                              text="Новое обращение от пользователя! Текст:")
            await bot.global_bot.send_message(chat_id=current_user.chat_id,
                                              text=text)


def call_user_back_request(number: str):
    log.logger.log('New call request: ' + number, log.MsgType.info, 'external services')
