from aiogram import Dispatcher
from bot.handlers.user.commands import user_router
from bot.handlers.admin.commands import admin_router
from bot.handlers.user.add_stickers import router as add_stickers_router

import logging

logger = logging.getLogger("bot")

def setup_routers(dp: Dispatcher):
    dp.include_router(add_stickers_router)
    logger.info("Подключаем роутер админа")
    dp.include_router(admin_router)
    logger.info("Подключаем роутер пользователя")
    dp.include_router(user_router)