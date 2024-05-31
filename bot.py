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
    UserToAdminReply = 4


class BotStatus:
    incoming_msg_type = IncomingMessageTypes.NotWaiting
    incoming_msg = None


class CallbackData(enum.Enum):
    start__support = 'start__support'
    start__get_call = 'start__get_call'

    start_adm__show_messages = 'start_adm__show_messages:'
    start_adm__close_ticket = 'start_adm__close_ticket:'
    start_adm__reply = 'start_adm__reply:'

    start_adm__remove_call_request = 'start_adm__remove_call_request'

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
        await external_services.send_to_support(
            await user.User.get_by_id(update.effective_user.id), update.message.text)
        await update.message.reply_text(text='Ваше сообщение передано поддержке. ')
        BotStatus.incoming_msg_type = IncomingMessageTypes.NotWaiting
        BotStatus.incoming_msg = None
        return

    if BotStatus.incoming_msg_type == IncomingMessageTypes.CallUserBack:
        await external_services.call_user_back_request(update.message.text)
        await update.message.reply_text(text='Звонок заказан! ')
        BotStatus.incoming_msg_type = IncomingMessageTypes.NotWaiting
        BotStatus.incoming_msg = None
        return

    if BotStatus.incoming_msg_type == IncomingMessageTypes.NotWaiting:
        log.logger.log('Got new unrecognized message: ' + update.message.text, log.MsgType.warn, 'bot')
        await update.message.reply_text('Главное меню: /start')
        return

    if BotStatus.incoming_msg_type == IncomingMessageTypes.AdminToUserReply:
        ticket = await support_ticket.get_by_admin(update.effective_user.id)
        if ticket is None:
            await update.effective_chat.send_message('Обращение не найдено. ')
        await ticket.to_user(update.message.text)

    if BotStatus.incoming_msg_type == IncomingMessageTypes.UserToAdminReply:
        ticket = await support_ticket.get_by_invoker(update.effective_user.id)
        if ticket is None:
            await update.effective_chat.send_message('Обращение не найдено. ')
        await ticket.to_admin(update.message.text)


async def cmd_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(text='Комана не распознана! ')
    log.logger.log('Got new unrecognized command: ' + update.message.text, log.MsgType.warn, 'bot')
    log.logger.log('Author: ' + str(update.effective_user.id), log.MsgType.warn, 'bot')


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == CallbackData.start__support.value:
        if await support_ticket.get_by_invoker(update.effective_user.id):
            await update.get_bot().send_message(chat_id=update.effective_chat.id,
                                                text='Вы уже открыли обращение. Дождитесь ответа администратора')
        else:
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

    if query.data == CallbackData.ticket__usr_reply.value:
        await query.edit_message_text(text=f"Введите ответ администратору: ")
        BotStatus.incoming_msg_type = IncomingMessageTypes.UserToAdminReply
        return

    if query.data == CallbackData.ticket__close.value:
        ticket = await support_ticket.get_by_admin(query.from_user.id)
        if ticket is None:
            await update.effective_chat.send_message('Обращение не найдено. ')
        await ticket.close(True)
        return

    if query.data == CallbackData.ticket__usr_close.value:
        ticket = await support_ticket.get_by_invoker(query.from_user.id)
        if ticket is None:
            await update.effective_chat.send_message('Обращение не найдено. ')
        await ticket.close(False)
        return

    if query.data == CallbackData.start_adm__remove_call_request.value:
        removed = support_ticket.call_requests[0]
        support_ticket.call_requests.remove(removed)
        await update.effective_chat.send_message(removed + ' был удален из списка. ')
        return

    if query.data.startswith('start_adm__show_messages'):
        ticket = await support_ticket.get_by_id(int(query.data.split(':')[1]))
        if ticket is None:
            await update.effective_chat.send_message('Обращение не найдено. ')
        for msg in ticket.messages:
            msg_admin = 'Сообщение от ' + ('администратора' if msg.sender.tg_user.id == update.effective_user.id
                                           else 'пользователя')
            msg_admin += '\n'
            msg_admin += 'Время отправки: ' + msg.datetime + '\n\n'
            msg_admin += msg.text
            await update.effective_chat.send_message(msg_admin)
            await update.effective_chat.send_message('Конец диалога. ')

        return

    if query.data.startswith('start_adm__close_ticket'):
        ticket = await support_ticket.get_by_id(int(query.data.split(':')[1]))
        if ticket is None:
            await update.effective_chat.send_message('Обращение не найдено. ')
        await ticket.close(True)

    if query.data.startswith('start_adm__reply'):
        await query.edit_message_text(text=f"Введите ответ пользователю: ")
        BotStatus.incoming_msg_type = IncomingMessageTypes.AdminToUserReply
        return


# endregion

# region commands

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await user.User.user_registered(update.effective_user.id):
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="Используйте /register, чтобы зарегистрироваться в системе. ")
        return

    role = await user.User.get_role(update.effective_user.id)
    if role == user.AccountLevel.User:
        keyboard = [
            [InlineKeyboardButton("Написать в поддержку", callback_data=CallbackData.start__support.value)],
            [InlineKeyboardButton("Забронировать обратный звонок", callback_data=CallbackData.start__get_call.value)],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="Этот бот передаст ваши сообщения поддержке!",
                                       reply_markup=reply_markup)
    elif role == user.AccountLevel.Admin:
        tickets = await support_ticket.get_admin_tickets(update.effective_user.id)

        msg_call = '\n\nОжидают звонка: \n\n'

        keyboard = [
            [InlineKeyboardButton("Отметить следующий вызов",
                                  callback_data=CallbackData.start_adm__remove_call_request.value)]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        for number in support_ticket.call_requests:
            msg_call += number + '\n'
        if msg_call == '\n\nОжидают звонка: \n\n':
            msg_call += 'Нет.'
            reply_markup = InlineKeyboardMarkup([])

        await update.effective_chat.send_message(text=msg_call, reply_markup=reply_markup)

        if len(tickets) == 0:
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text="Открытых обращений нет! ")
            return

        for ticket in tickets:
            if ticket.messages is []:
                await update.effective_chat.send_message(text='История сообщений не сохранилась. ')
                return

            msg = "Обращение " + str(ticket.ticket_id) + ":\n\n"
            msg += "Статус:\t"

            keyboard = [
                [InlineKeyboardButton("Показать сообщения",
                                      callback_data=CallbackData.start_adm__show_messages.value +
                                      str(ticket.ticket_id))],
                [InlineKeyboardButton("Закрыть обращение",
                                      callback_data=CallbackData.start_adm__close_ticket.value +
                                      str(ticket.ticket_id))]
            ]

            try:
                if ticket.messages[-1].sender.tg_user.id == update.effective_user.id:
                    msg += "Ожидается ответ пользователя..."
                else:
                    msg += "Ожидается ответ администратора... "
                    keyboard.append([InlineKeyboardButton("Ответить",
                                                          callback_data=CallbackData.start_adm__reply.value +
                                                          str(ticket.ticket_id))])
            except IndexError:
                msg += "Неизвестно. "
                keyboard.append([InlineKeyboardButton("Ответить",
                                                      callback_data=CallbackData.start_adm__reply.value +
                                                      str(ticket.ticket_id))])

            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.effective_chat.send_message(text=msg, reply_markup=reply_markup)


async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await user.User.user_registered(update.effective_user.id):
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

    log.logger.log("Bot starting... \n", log.MsgType.success, 'Bot', '\n')
    try:
        application.run_polling()
    except telegram.error.NetworkError:
        log.logger.log('Network is unreachable. Aborting... ', log.MsgType.critical, 'bot')


def add_command(bot: telegram.ext.Application, cmd: str, func: ()):
    handler = CommandHandler(cmd, func)
    bot.add_handler(handler)
    log.logger.log(f'*{cmd}* is added! ', log.MsgType.success, 'bot')

# endregion
