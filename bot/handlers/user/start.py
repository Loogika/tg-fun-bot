import logging
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from storage.google_sheets import add_user_if_not_exists
from bot.handlers.user.constants import (
    BTN_CREATE_PACK, BTN_EDIT_PACK,
    CB_STICKERS_CREATE, CB_STICKERS_EDIT,
    TEXT_START_MENU
)

logger = logging.getLogger("bot")

def start_menu_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text=BTN_CREATE_PACK, callback_data=CB_STICKERS_CREATE)
    kb.button(text=BTN_EDIT_PACK, callback_data=CB_STICKERS_EDIT)
    kb.adjust(1)
    return kb.as_markup()

async def send_start_menu(message: Message):
    await message.answer(TEXT_START_MENU, reply_markup=start_menu_kb())

async def start_handler(message: Message):
    user = message.from_user
    add_user_if_not_exists(user.id, user.username)
    await send_start_menu(message)

async def message_logger_handler(message: Message):
    user = message.from_user
    username = user.username or "Unknown"
    text = message.text or "<не текстовое сообщение>"
    logger.info("Пользователь %s (%s) написал: %s", username, user.id, text)