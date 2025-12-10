from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from config import ADMIN_ID
from bot.admin.handlers import broadcast_handler
import logging

logger = logging.getLogger("bot")

admin_router = Router()

@admin_router.message(Command("broadcast"))
async def admin_broadcast_wrapper(message: Message, bot):
    if message.from_user.id != ADMIN_ID:
        logger.info(f"Пользователь {message.from_user.username} попытался вызвать команду для админа")
        await message.answer("Эта команда только для админа.")
        return

    logger.info(f"Admin {message.from_user.username}:  {message.text}")
    await broadcast_handler(message, bot)