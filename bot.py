import os
import sys
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

import log


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")


def init(token):
    # Telegram
    application = ApplicationBuilder().token(token).build()

    log.logger.log("Bot starting... ", log.MsgType.info, 'Bot')
    application.run_polling()
