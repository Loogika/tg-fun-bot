from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram import F
from bot.handlers.user.core import start_handler, message_logger_handler, ADD_STICKERS_BTN_TEXT
from bot.handlers.user.core import send_start_menu
from storage.google_sheets import add_pack_to_user

import logging

from bot.fsm.add_sticker import AddStickerFSM

logger = logging.getLogger("bot")
user_router = Router()

# Регистрируем команду /start
user_router.message.register(start_handler, Command("start"))

@user_router.message(Command("stop"))
async def stop_cmd(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Ок, остановил процесс.")
    await send_start_menu(message)

# Логирование сообщений
# @user_router.message()
# async def log_user_message(message: Message):
#     await message_logger_handler(message)

# STREAM handler заглушка
@user_router.message(AddStickerFSM.STREAM)
async def stream_handler(message: Message, state: FSMContext):
    if message.sticker:
        await message.answer("Получен стикер")
    elif message.photo:
        await message.answer("Получено фото")
    elif message.document and message.document.mime_type.startswith("image/"):
        await message.answer("Получен документ-изображение")
    elif message.text:
        await message.answer("Получен текст (можно для emoji позже)")
    else:
        await message.answer("Неизвестный тип сообщения")


def pack_open_kb(pack_name: str):
    kb = InlineKeyboardBuilder()
    kb.button(text="📦 Открыть стикерпак", url=f"https://t.me/addstickers/{pack_name}")
    kb.adjust(1)
    return kb.as_markup()

@user_router.message(AddStickerFSM.WAIT_PACK)
async def set_pack_name(message: Message, state: FSMContext):
    logger.info("SET_PACK_NAME: user_id=%s text=%r", message.from_user.id, message.text)

    pack_name = message.text.strip()
    await state.update_data(pack_name=pack_name)
    await state.set_state(AddStickerFSM.STREAM)

    packs = add_pack_to_user(message.from_user.id, pack_name)
    logger.info("PACK_ADDED: user_id=%s pack=%s packs=%s", message.from_user.id, pack_name, packs)

    await message.answer(f"Пак выбран: {pack_name}\nТеперь отправляй стикеры или картинки.")




@user_router.callback_query(F.data == "stickers:create")
async def cb_create_pack(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(AddStickerFSM.WAIT_PACK)
    await call.message.answer(
        "Ок. Пришли short_name для НОВОГО пака.\n"
        "Пример: my_pack_by_bot\n\n"
        "Остановить: /stop"
    )
    await call.answer()

@user_router.callback_query(F.data == "stickers:edit")
async def cb_edit_pack(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(AddStickerFSM.WAIT_PACK)
    await call.message.answer(
        "Пришли short_name СУЩЕСТВУЮЩЕГО пака.\n"
        "Пример: my_pack_by_bot\n\n"
        "Остановить: /stop"
    )
    await call.answer()
