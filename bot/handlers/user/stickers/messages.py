import logging

from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

from bot.fsm.add_sticker import AddStickerFSM
from storage.google_sheets import get_user_packs, add_pack_to_user
from bot.handlers.user.start import send_start_menu
from bot.handlers.user.stickers.keyboards import stream_kb, packs_select_kb, pack_open_kb
from bot.handlers.user.constants import (
    TEXT_STOPPED,
    TEXT_PACK_CHOSEN,
)

# НАПИСАТЬ ЛОГИ
logger = logging.getLogger("bot")

router = Router()

@router.message(Command("stop"))
async def cmd_stop(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(TEXT_STOPPED)
    await send_start_menu(message)

@router.message(AddStickerFSM.STREAM, ~Command())
async def msg_stream(message: Message, state: FSMContext):
    data = await state.get_data()
    pack_name = data.get("pack_name")

    if message.sticker:
        text = "Получен стикер"
    elif message.photo:
        text = "Получено фото"
    elif message.document and message.document.mime_type and message.document.mime_type.startswith("image/"):
        text = "Получен документ-изображение"
    elif message.text:
        text = "Получен текст (позже можно использовать для emoji)"
    else:
        text = "Неизвестный тип сообщения"

    await message.answer(text, reply_markup=stream_kb(pack_name))


@router.message(AddStickerFSM.WAIT_PACK)
async def msg_set_pack_name(message: Message, state: FSMContext):
    data = await state.get_data()
    mode = data.get("mode")

    # Режим редактирования: только выбор кнопкой, текст игнорируем
    if mode == "edit":
        packs = get_user_packs(message.from_user.id)
        if not packs:
            await message.answer("У тебя пока нет сохранённых паков. Сначала создай новый.")
            await send_start_menu(message)
            return

        await message.answer("Выбирай пак кнопкой:", reply_markup=packs_select_kb(packs))
        return

    # Режим создания: принимаем short_name текстом
    pack_name = (message.text or "").strip()
    if not pack_name:
        await message.answer("Пришли short_name текстом.")
        return

    await state.update_data(pack_name=pack_name)
    await state.set_state(AddStickerFSM.STREAM)

    # Пока сохраняем сразу. Позже лучше сохранять после реального createNewStickerSet.
    add_pack_to_user(message.from_user.id, pack_name)

    await message.answer(
        TEXT_PACK_CHOSEN.format(pack_name=pack_name),
        reply_markup=pack_open_kb(pack_name),
    )