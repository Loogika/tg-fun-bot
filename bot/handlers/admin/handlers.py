import asyncio
import logging
from aiogram.types import Message
from storage.google_sheets import get_all_user_ids
import logging

logger = logging.getLogger("bot")

async def broadcast_handler(message: Message, bot):
    full_text = message.text or ""
    parts = full_text.split(maxsplit=1)

    if len(parts) < 2:
        await message.answer(
            "Напиши текст после команды.\n"
            "Пример:\n/broadcast Привет!"
        )
        return

    text_to_send = parts[1]
    user_ids = get_all_user_ids()

    sent, failed = 0, 0
    await message.answer(f"Начинаю рассылку {len(user_ids)} пользователям...")

    for uid in user_ids:
        try:
            await bot.send_message(uid, text_to_send)
            sent += 1
            await asyncio.sleep(0.05)
        except Exception as e:
            logger.exception(e)
            failed += 1

    await message.answer(
        f"Готово!\nОтправлено: {sent}\nОшибок: {failed}"
    )