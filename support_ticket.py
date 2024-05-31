import datetime
import random

import persistence
import user
import bot

from typing import List
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


class Message:
    sender: user.User
    receiver: user.User
    text: str
    datetime: str

    def __init__(self, sender: user.User, receiver: user.User, text: str, date_time: str):
        self.sender = sender
        self.receiver = receiver
        self.text = text
        self.datetime = date_time

    async def send(self, caption, reply_markup):
        await bot.global_bot.send_message(chat_id=self.receiver.chat_id, text=caption + self.text,
                                          reply_markup=reply_markup)


class Ticket:
    invoker: user.User
    administrator: user.User
    messages: List[Message] = list()
    ticket_id: int

    def __init__(self, invoker: user.User, admin: user.User):
        self.invoker = invoker
        self.administrator = admin

        self.ticket_id = random.randint(1, 9999999)
        while self.ticket_id in map(self.get_id, tickets):
            self.ticket_id = random.randint(1, 9999999)

    async def get_admin_id(self):
        return self.administrator.tg_user.id

    async def send_hello_to_admin(self):
        new_msg = Message(self.invoker, self.administrator, 'Создано новое обращение: ' + str(self.ticket_id),
                          date_time=datetime.datetime.now().strftime('%d/%m/%Y %H:%M '))
        await new_msg.send('', InlineKeyboardMarkup([]))

    def get_id(self):
        return self.ticket_id

    async def to_admin(self, text):
        keyboard = [
            [InlineKeyboardButton("Ответить", callback_data=bot.CallbackData.ticket__reply.value)],
            [InlineKeyboardButton("Закрыть", callback_data=bot.CallbackData.ticket__close.value)],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        msg = Message(self.invoker, self.administrator, text,
                      date_time=datetime.datetime.now().strftime('%d/%m/%Y %H:%M '))
        self.messages.append(msg)
        await msg.send(f'Новое сообщение ({self.ticket_id}) от пользователя: \n\n', reply_markup)

    async def to_user(self, text):
        keyboard = [
            [InlineKeyboardButton("Ответить", callback_data=bot.CallbackData.ticket__usr_reply.value)],
            [InlineKeyboardButton("Закрыть обращение", callback_data=bot.CallbackData.ticket__usr_close.value)],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        msg = Message(self.administrator, self.invoker, text,
                      date_time=datetime.datetime.now().strftime('%d/%m/%Y %H:%M '))
        self.messages.append(msg)
        await msg.send('Новое сообщение от администратора: \n\n', reply_markup)
        await bot.global_bot.send_message(chat_id=self.administrator.chat_id, text='Ответ передан пользователю. ')

    def add_msg(self, invoker, admin, text: str):
        self.messages.append(Message(invoker, admin, text,
                                     date_time=datetime.datetime.now().strftime('%d/%m/%Y %H:%M ')))

    async def close(self, closed_by_admin: bool):
        self.messages.clear()
        tickets.remove(self)
        persistence.write(tickets)
        text = 'Обращение %n закрыто'
        if closed_by_admin:
            text += ' администратором. '
        else:
            text += ' пользователем. '
        await bot.global_bot.send_message(chat_id=self.invoker.chat_id, text=text.replace('%n ', ''))
        await bot.global_bot.send_message(chat_id=self.administrator.chat_id, text=text.replace('%n',
                                                                                                str(self.ticket_id)))


async def get_by_invoker(uid: int):
    for _ticket in tickets:
        if _ticket.invoker.tg_user.id == uid:
            return _ticket


async def get_by_admin(uid: int):
    for _ticket in tickets:
        if _ticket.administrator.tg_user.id == uid:
            return _ticket


async def get_admin_tickets(uid: int):
    result = []
    for _ticket in tickets:
        if _ticket.administrator.tg_user.id == uid:
            result.append(_ticket)
    return result


async def get_by_id(uid: int) -> Ticket:
    for ticket in tickets:
        if ticket.ticket_id == uid:
            return ticket


tickets: List[Ticket] = list()
call_requests: List[str] = list()
