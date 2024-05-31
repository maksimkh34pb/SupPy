import enum
import telegram.ext
import external_services
import log
import support_ticket
import user

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, ExtBot

global_bot: ExtBot


# region bot classes

class IncomingMessageTypes(enum.Enum):
    NotWaiting = 0
    NewMessageToSupport = 1
    CallUserBack = 2
    AdminToUserReply = 3


class BotStatus:
    incoming_msg_type = IncomingMessageTypes.NotWaiting
    incoming_msg = None


class CallbackData(enum.Enum):
    start__support = 'start__support'
    start__get_call = 'start__get_call'

    register__user = 'register__user'
    register__admin = 'register__admin'

    ticket__reply = 'ticket__reply'
    ticket__close = 'ticket__close'

    ticket__usr_reply = 'ticket__usr_reply'
    ticket__usr_close = 'ticket__usr_close'


# endregion

# region bot handlers


async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if BotStatus.incoming_msg_type == IncomingMessageTypes.NewMessageToSupport:
        await external_services.send_to_support(user.User.get_by_id(update.effective_user.id), update.message.text)
        await update.message.reply_text(text='Ваше сообщение передано поддержке. ')
        BotStatus.incoming_msg_type = IncomingMessageTypes.NotWaiting
        BotStatus.incoming_msg = None
        return

    if BotStatus.incoming_msg_type == IncomingMessageTypes.CallUserBack:
        external_services.call_user_back_request(update.message.text)
        await update.message.reply_text(text='Звонок заказан! ')
        BotStatus.incoming_msg_type = IncomingMessageTypes.NotWaiting
        BotStatus.incoming_msg = None
        return

    if BotStatus.incoming_msg_type == IncomingMessageTypes.NotWaiting:
        log.logger.log('Got new text message: ' + update.message.text, log.MsgType.warn, 'bot')
        await update.message.reply_text('Главное меню: /start')
        return

    if BotStatus.incoming_msg_type == IncomingMessageTypes.AdminToUserReply:
        ticket = support_ticket.Ticket.get_by_admin(update.effective_user.id)
        await ticket.reply_to_user(update.message.text)


async def cmd_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(text='Комана не распознана! ')


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == CallbackData.start__support.value:
        await query.edit_message_text(text=f"Напишите свое сообщение поддержке: ")
        BotStatus.incoming_msg_type = IncomingMessageTypes.NewMessageToSupport
        return

    if query.data == CallbackData.start__get_call.value:
        await query.edit_message_text(text=f"Укажите свой телефон для обратного звонка: ")
        BotStatus.incoming_msg_type = IncomingMessageTypes.CallUserBack
        return

    if query.data == CallbackData.register__user.value:
        user.User(chat_id=update.effective_chat.id, level=user.AccountLevel.User, user=query.from_user)
        await query.edit_message_text('Вы зарегистрированы как пользователь! ')
        return

    if query.data == CallbackData.register__admin.value:
        user.User(chat_id=update.effective_chat.id, level=user.AccountLevel.Admin, user=query.from_user)
        await query.edit_message_text('Вы зарегистрированы как администратор! ')
        return

    if query.data == CallbackData.ticket__reply.value:
        await query.edit_message_text(text=f"Введите ответ пользователю: ")
        BotStatus.incoming_msg_type = IncomingMessageTypes.AdminToUserReply
        return

    if query.data == CallbackData.ticket__close.value:
        ticket = support_ticket.Ticket.get_by_admin(query.from_user.id)
        ticket.close()
        await query.edit_message_text(text=f"Обращение закрыто. ")
        await global_bot.send_message(ticket.invoker.chat_id, 'Обращение закрыто администратором. ')

    if query.data == CallbackData.ticket__usr_reply.value:
        await query.edit_message_text(text=f"Введите ответ администратору: ")
        BotStatus.incoming_msg_type = IncomingMessageTypes.NewMessageToSupport
        return

    if query.data == CallbackData.ticket__usr_close.value:
        ticket = support_ticket.Ticket.get_by_invoker(query.from_user.id)
        ticket.close()
        await query.edit_message_text(text=f"Обращение закрыто. ")
        await global_bot.send_message(ticket.administrator.chat_id, 'Обращение закрыто пользователем. ')


# endregion

# region commands

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not user.User.user_registered(update.effective_user.id):
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="Используйте /register, чтобы зарегистрироваться в системе. ")
        return

    role = user.User.get_role(update.effective_user.id)
    if role == user.AccountLevel.User:
        keyboard = [
            [InlineKeyboardButton("Написать в поддержку", callback_data=CallbackData.start__support.value)],
            [InlineKeyboardButton("Забронировать обратный звонок", callback_data=CallbackData.start__get_call.value)],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        log.logger.log(f'User {update.effective_chat.username}:{update.effective_chat.id} started bot! ',
                       log.MsgType.info, 'bot')
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="Этот бот передаст ваши сообщения поддержке!",
                                       reply_markup=reply_markup)
    elif role == user.AccountLevel.Admin:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="Новых обращений нет! ")


async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if user.User.user_registered(update.effective_user.id):
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="Вы уже зарегистрированы! ")
        return
    keyboard = [
        [InlineKeyboardButton("Пользователь", callback_data=CallbackData.register__user.value)],
        [InlineKeyboardButton("Администратор", callback_data=CallbackData.register__admin.value)],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Выберите вашу роль: ",
                                   reply_markup=reply_markup)


# endregion

# region functional


def init(token):
    #
    #   Telegram
    #

    application = ApplicationBuilder().token(token).build()

    # adding commands

    add_command(application, 'start', start)
    add_command(application, 'register', register)

    application.add_handler(CallbackQueryHandler(callback_handler))
    application.add_handler(MessageHandler(telegram.ext.filters.COMMAND, cmd_handler))
    application.add_handler(MessageHandler(telegram.ext.filters.TEXT, text_handler))

    global global_bot
    global_bot = application.bot

    log.logger.log("Bot starting... ", log.MsgType.success, 'Bot')
    try:
        application.run_polling()
    except telegram.error.NetworkError:
        log.logger.log('Network is unreachable. Aborting... ', log.MsgType.critical, 'bot')


def add_command(bot: telegram.ext.Application, cmd: str, func: ()):
    handler = CommandHandler(cmd, func)
    bot.add_handler(handler)
    log.logger.log(f'*{cmd}* is added! ', log.MsgType.success, 'bot')

# endregion
