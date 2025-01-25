import logging
from aiogram import BaseMiddleware
from aiogram.types import Message
from config_reader import LOG_LEVEL

# logging.basicConfig(level=LOG_LEVEL)

class LoggingMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Message, data: dict) -> None:
        if isinstance(event, Message):
            user_id = event.from_user.id
            message_text = event.text

            print(f"Получено сообщение: '{message_text}' от пользователя: {user_id}")
            # logging.info(f"Получено сообщение: '{message_text}' от пользователя: {user_id}")

        await handler(event, data)
