from aiogram.types import Message
from storage.google_sheets import add_user_if_not_exists
import logging

logger = logging.getLogger("bot")

async def start_handler(message: Message):
    user = message.from_user
    add_user_if_not_exists(user.id, user.username)

    await message.answer(
        "Привет! Ты зарегистрирован в системе 🐰\n"
        "Твой id записан в Google Sheets."
    )

# --- Обработка всех остальных сообщений ---
async def message_logger_handler(message: Message):
    user = message.from_user
    username = user.username or "Unknown"
    text = message.text or "<не текстовое сообщение>"

    logger.info(f"Пользователь {username} ({user.id}) написал: {text}")

    # Можно отвечать или не отвечать пользователю
    # await message.answer("Сообщение получено!")