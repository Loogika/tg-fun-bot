from aiogram import Router
from aiogram.filters import Command
from bot.handlers.user.start import start_handler
from bot.handlers.user.stickers.callbacks import router as stickers_cb
from bot.handlers.user.stickers.messages import router as stickers_msg

user_router = Router()
user_router.include_router(stickers_cb)
user_router.include_router(stickers_msg)

user_router.message.register(start_handler, Command("start"))