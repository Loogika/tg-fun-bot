from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from config import ADMIN_ID
from bot.user.handlers import start_handler, message_logger_handler
import logging

logger = logging.getLogger("bot")
user_router = Router()

# Регистрируем команду /start
user_router.message.register(start_handler, Command("start"))

# Логирование сообщений, кроме админа
@user_router.message()
async def log_user_message(message: Message):
    if message.from_user.id == ADMIN_ID:
        return  # админ не должен попадать сюда
    await message_logger_handler(message)