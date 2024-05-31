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


class Ticket:
    invoker: user.User
    administrator: user.User
    closed = False
    messages: List[Message] = list()

    def __init__(self, invoker: user.User, admin: user.User, text: str):
        self.invoker = invoker
        self.administrator = admin
        self.add_msg(invoker, admin, text)

    async def send_ticket(self, text: str):
        keyboard = [
            [InlineKeyboardButton("Ответить", callback_data=bot.CallbackData.ticket__reply.value)],
            [InlineKeyboardButton("Закрыть", callback_data=bot.CallbackData.ticket__close.value)],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await bot.global_bot.send_message(chat_id=self.administrator.chat_id,
                                          text=f"Новое сообщение от пользователя: "
                                               f"\n\n{text}",
                                          reply_markup=reply_markup)

    async def reply_to_user(self, text):
        keyboard = [
            [InlineKeyboardButton("Ответить", callback_data=bot.CallbackData.ticket__usr_reply.value)],
            [InlineKeyboardButton("Закрыть", callback_data=bot.CallbackData.ticket__usr_close.value)],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await bot.global_bot.send_message(chat_id=self.invoker.chat_id,
                                          text=f"Новое сообщение от администратора: "
                                               f"\n\n{text}",
                                          reply_markup=reply_markup)

    def add_msg(self, invoker, admin, text: str):
        self.messages.append(Message(invoker, admin, text))

    def close(self):
        self.closed = True

    @staticmethod
    def get_by_admin(uid: int):
        for _ticket in tickets:
            if _ticket.administrator.user.id == uid:
                return _ticket

    @staticmethod
    def get_by_invoker(uid: int):
        for _ticket in tickets:
            if _ticket.invoker.user.id == uid:
                return _ticket


tickets: List[Ticket] = list()
