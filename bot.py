import asyncio
import enum
import time

import telegram.ext
import log
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler


class IncomingMessageTypes(enum.Enum):
    NotWaiting = 0
    NewMessageToSupport = 1
    CallUserBack = 2


class BotStatus:
    incoming_msg_type = IncomingMessageTypes.NotWaiting
    incoming_msg = None


class CallbackDatas(enum.Enum):
    start__support = 'start__support'
    start__get_call = 'start__get_call'


async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if BotStatus.incoming_msg_type == IncomingMessageTypes.NewMessageToSupport:
        await update.message.reply_text(text='Ваше сообщение передано поддержке. ')
        BotStatus.incoming_msg_type = IncomingMessageTypes.NotWaiting
        BotStatus.incoming_msg = None
    if BotStatus.incoming_msg_type == IncomingMessageTypes.CallUserBack:
        await update.message.reply_text(text='Звонок заказан! ')
        BotStatus.incoming_msg_type = IncomingMessageTypes.NotWaiting
        BotStatus.incoming_msg = None
    if BotStatus.incoming_msg_type == IncomingMessageTypes.NotWaiting:
        log.logger.log('Got new text message: ' + update.message.text, log.MsgType.warn, 'bot')
        await update.message.reply_text('Главное меню: /start')


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Написать в поддержку", callback_data=CallbackDatas.start__support.value)],
        [InlineKeyboardButton("Забронировать обратный звонок", callback_data=CallbackDatas.start__get_call.value)],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    log.logger.log(f'User {update.effective_chat.username}:{update.effective_chat.id} started bot! ', log.MsgType.info, 'bot')
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Этот бот передаст ваши сообщения поддержке!",
                                   reply_markup=reply_markup)


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == CallbackDatas.start__support.value:
        await query.edit_message_text(text=f"Напишите свое сообщение поддержке: ")
        BotStatus.incoming_msg_type = IncomingMessageTypes.NewMessageToSupport
    if query.data == CallbackDatas.start__get_call.value:
        await query.edit_message_text(text=f"Укажите свой телефон для обратного звонка: ")
        BotStatus.incoming_msg_type = IncomingMessageTypes.CallUserBack


def init(token):
    #
    #   Telegram
    #

    application = ApplicationBuilder().token(token).build()

    # adding commands

    add_command(application, 'start', start)
    application.add_handler(CallbackQueryHandler(callback_handler))
    application.add_handler(MessageHandler(telegram.ext.filters.TEXT, text_handler))

    log.logger.log("Bot starting... ", log.MsgType.success, 'Bot')
    application.run_polling()


def add_command(bot: telegram.ext.Application, cmd: str, func: ()):
    handler = CommandHandler(cmd, func)
    bot.add_handler(handler)
    log.logger.log(f'*{cmd}* is added! ', log.MsgType.success, 'bot')
