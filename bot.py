import telegram.ext
import log
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log.logger.log('New message!', log.MsgType.info, 'bot')
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Этот бот передаст ваши сообщения поддержке!")


def init(token):
    #
    #   Telegram
    #

    application = ApplicationBuilder().token(token).build()

    # adding commands

    add_command(application, 'start', start)

    log.logger.log("Bot starting... ", log.MsgType.success, 'Bot')
    application.run_polling()


def add_command(bot: telegram.ext.Application, cmd: str, func: ()):
    handler = CommandHandler(cmd, func)
    bot.add_handler(handler)
    log.logger.log(f'*{cmd}* is added! ', log.MsgType.success, 'bot')
