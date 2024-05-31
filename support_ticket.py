import random

import user
import bot

from typing import List
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


class Message:
    sender: user.User
    receiver: user.User
    text: str

    def __init__(self, sender: user.User, receiver: user.User, text: str):
        self.sender = sender
        self.receiver = receiver
        self.text = text

    async def send(self, caption, reply_markup):
        await bot.global_bot.send_message(chat_id=self.receiver.chat_id, text=caption + self.text,
                                          reply_markup=reply_markup)


class Ticket:
    invoker: user.User
    administrator: user.User
    messages: List[Message] = list()
    ticket_id: int

    def __init__(self, invoker: user.User, admin: user.User, text: str):
        self.invoker = invoker
        self.administrator = admin

        self.ticket_id = random.randint(1, 9999999)
        while self.ticket_id in map(self.get_id, tickets):
            self.ticket_id = random.randint(1, 9999999)

    async def send_hello_to_admin(self):
        new_msg = Message(self.invoker, self.administrator, 'Создано новое обращение: ' + str(self.ticket_id))
        await new_msg.send('', InlineKeyboardMarkup([]))

    async def to_admin(self, text):
        keyboard = [
            [InlineKeyboardButton("Ответить", callback_data=bot.CallbackData.ticket__reply.value)],
            [InlineKeyboardButton("Закрыть", callback_data=bot.CallbackData.ticket__close.value)],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        msg = Message(self.invoker, self.administrator, text)
        self.messages.append(msg)
        await msg.send(f'Новое сообщение ({self.ticket_id}) от пользователя: \n\n', reply_markup)

    def get_id(self):
        return self.ticket_id

    async def to_user(self, text):
        keyboard = [
            [InlineKeyboardButton("Ответить", callback_data=bot.CallbackData.ticket__usr_reply.value)],
            [InlineKeyboardButton("Закрыть обращение", callback_data=bot.CallbackData.ticket__usr_close.value)],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        msg = Message(self.administrator, self.invoker, text)
        self.messages.append(msg)
        await msg.send('Новое сообщение от администратора: \n\n', reply_markup)

    def add_msg(self, invoker, admin, text: str):
        self.messages.append(Message(invoker, admin, text))

    async def close(self, closed_by_admin: bool):
        tickets.remove(self)
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
        if _ticket.invoker.user.id == uid:
            return _ticket


async def get_by_admin(uid: int):
    for _ticket in tickets:
        if _ticket.administrator.user.id == uid:
            return _ticket


tickets: List[Ticket] = list()
