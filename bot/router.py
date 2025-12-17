from aiogram import Dispatcher
from bot.handlers.user.router import user_router
# from bot.handlers.admin.commands import admin_router

import logging

logger = logging.getLogger("bot")

#Метод отвечающий за подключение написанных нами роутеров
#Если оба роутера могут обработать одно и то-же сообщение, то сработает тот, что стоит первее
def setup_routers(dp: Dispatcher):
    # logger.info("Подключаем роутер админа")
    # dp.include_router(admin_router)
    logger.info("Подключаем роутер пользователя")
    dp.include_router(user_router)