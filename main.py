import asyncio
import time
import logging
from typing import List

from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command

import gspread
from google.oauth2.service_account import Credentials

import os
from dotenv import load_dotenv


load_dotenv()

# ------------ ЛОГИРОВАНИЕ ------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# ------------ НАСТРОЙКИ ------------

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE")

# ------------ ИНИЦИАЛИЗАЦИЯ GOOGLE SHEETS ------------

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

logger.info("Инициализация Google Sheets...")
creds = Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=SCOPES
)
gclient = gspread.authorize(creds)
sheet = gclient.open_by_key(SPREADSHEET_ID).sheet1  # первый лист
logger.info("Google Sheets инициализированы успешно.")


def add_user_if_not_exists(user_id: int, username: str | None) -> None:
    str_user_id = str(user_id)
    logger.info(f"Проверяю наличие пользователя {str_user_id} в таблице...")

    col_user_ids = sheet.col_values(1)  # A колонка

    if str_user_id in col_user_ids:
        logger.info(f"Пользователь {str_user_id} уже есть в таблице.")
        return

    sheet.append_row([
        str_user_id,
        username or "",
        time.strftime("%Y-%m-%d %H:%M:%S")
    ])
    logger.info(f"Добавлен новый пользователь {str_user_id} ({username}) в таблицу.")


def get_all_user_ids() -> List[int]:
    col_user_ids = sheet.col_values(1)
    logger.info(f"Считан столбец user_id из таблицы: {col_user_ids}")
    result = []
    for value in col_user_ids:
        try:
            result.append(int(value))
        except ValueError:
            logger.warning(f"Не получилось привести '{value}' к int, пропускаю.")
    logger.info(f"Итого валидных user_id: {len(result)} -> {result}")
    return result


# ------------ НАСТРОЙКА БОТА ------------

bot = Bot(TELEGRAM_BOT_TOKEN)
dp = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(message: Message):
    user = message.from_user
    logger.info(f"Команда /start от {user.id} (@{user.username})")

    add_user_if_not_exists(user.id, user.username)

    await message.answer(
        "Привет! Ты зарегистрирован в системе 🐰\n"
        "Твой id записан в Google Sheets."
    )


@dp.message(Command("broadcast"))
async def cmd_broadcast(message: Message):
    logger.info(f"Команда /broadcast от {message.from_user.id}: {message.text!r}")

    if message.from_user.id != ADMIN_ID:
        logger.warning(f"Пользователь {message.from_user.id} не является админом.")
        await message.answer("Эта команда только для админа.")
        return

    full_text = message.text or ""
    parts = full_text.split(maxsplit=1)

    if len(parts) < 2:
        logger.warning("У /broadcast нет текста после команды.")
        await message.answer("Напиши текст после команды.\nНапример:\n/broadcast Привет всем!")
        return

    text_to_send = parts[1]
    logger.info(f"Текст для рассылки: {text_to_send!r}")

    user_ids = get_all_user_ids()
    await message.answer(f"Начинаю рассылку {len(user_ids)} пользователям...")
    logger.info(f"Начинаю рассылку {len(user_ids)} пользователям: {user_ids}")

    sent = 0
    failed = 0

    for uid in user_ids:
        try:
            logger.info(f"Пытаюсь отправить сообщение пользователю {uid}...")
            await bot.send_message(uid, text_to_send)
            sent += 1
            logger.info(f"Успешно отправлено пользователю {uid}.")
            await asyncio.sleep(0.05)
        except Exception as e:
            logger.exception(f"Не удалось отправить {uid}: {e}")
            failed += 1

    await message.answer(
        f"Готово!\n"
        f"Отправлено: {sent}\n"
        f"Ошибок: {failed}"
    )
    logger.info(f"Рассылка завершена. Отправлено: {sent}, Ошибок: {failed}")


async def main():
    logger.info("Запускаю polling бота...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
