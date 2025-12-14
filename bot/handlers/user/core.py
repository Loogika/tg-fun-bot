from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from storage.google_sheets import add_user_if_not_exists
import logging

logger = logging.getLogger("bot")
ADD_STICKERS_BTN_TEXT = "➕ Добавить стикеры"


def start_menu_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="🆕 Создать стикерпак", callback_data="stickers:create")
    kb.button(text="✏️ Редактировать существующий", callback_data="stickers:edit")
    kb.adjust(1)
    return kb.as_markup()

# Проверка регистрации пользователя при команде /start
async def start_handler(message: Message):
    user = message.from_user
    add_user_if_not_exists(user.id, user.username)
    await send_start_menu(message)

# Последующая точка входа после /start или /stop
async def send_start_menu(message: Message):
    await message.answer("Что делаем?", reply_markup=start_menu_kb())

# --- Обработка всех остальных сообщений ---
async def message_logger_handler(message: Message):
    user = message.from_user
    username = user.username or "Unknown"
    text = message.text or "<не текстовое сообщение>"

    logger.info(f"Пользователь {username} ({user.id}) написал: {text}")

    # Можно отвечать или не отвечать пользователю
    # await message.answer("Сообщение получено!")