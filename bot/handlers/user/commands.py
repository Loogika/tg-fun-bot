from aiogram import Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram import F
from bot.handlers.user.core import start_handler, message_logger_handler, ADD_STICKERS_BTN_TEXT
from bot.handlers.user.core import send_start_menu
from storage.google_sheets import add_pack_to_user, get_user_packs


import logging

from bot.fsm.add_sticker import AddStickerFSM

# Подключаем логинг
logger = logging.getLogger("bot")

# Регистрируем роутер, который будет отвечать за написанные ниже команды
user_router = Router()

# Регистрируем команду /start
user_router.message.register(start_handler, Command("start"))

# Команда /stop
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

def pack_open_kb(pack_name: str):
    kb = InlineKeyboardBuilder()
    kb.button(text="📦 Открыть стикерпак", url=f"https://t.me/addstickers/{pack_name}")
    kb.adjust(1)
    return kb.as_markup()

def packs_select_kb(packs: list[str]):
    kb = InlineKeyboardBuilder()
    for i, name in enumerate(packs[:20]):  # ограничим, чтобы не раздувать
        kb.button(text=name, callback_data=f"stickers:pick:{i}")
    kb.adjust(1)
    return kb.as_markup()

@user_router.message(AddStickerFSM.WAIT_PACK)
async def set_pack_name(message: Message, state: FSMContext):
    data = await state.get_data()
    mode = data.get("mode")

    if mode == "edit":
        packs = get_user_packs(message.from_user.id)
        await message.answer("Выбирай пак кнопкой:", reply_markup=packs_select_kb(packs))
        return

    # mode == "create"
    pack_name = message.text.strip()
    await state.update_data(pack_name=pack_name)
    await state.set_state(AddStickerFSM.STREAM)

    add_pack_to_user(message.from_user.id, pack_name)

    await message.answer(
        f"Пак выбран: {pack_name}\nТеперь отправляй стикеры или картинки.",
        reply_markup=pack_open_kb(pack_name)
    )

def stream_kb(pack_name: str | None = None) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    if pack_name:
        kb.button(text="📦 Открыть пак", url=f"https://t.me/addstickers/{pack_name}")
    kb.button(text="⛔ Остановить редактирование", callback_data="stickers:stop_edit")
    kb.adjust(1)
    return kb.as_markup()

@user_router.callback_query(F.data == "stickers:stop_edit")
async def cb_stop_edit(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.answer("Ок, остановил редактирование.")
    await send_start_menu(call.message)
    await call.answer()

@user_router.callback_query(F.data == "stickers:create")
async def cb_create_pack(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.update_data(mode="create")
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
    await state.update_data(mode="edit")
    await state.set_state(AddStickerFSM.WAIT_PACK)

    packs = get_user_packs(call.from_user.id)
    if not packs:
        await call.message.answer("У тебя пока нет сохранённых паков. Сначала создай новый.")
        await send_start_menu(call.message)
        await call.answer()
        return

    await call.message.answer("Выбери стикерпак:", reply_markup=packs_select_kb(packs))
    await call.answer()

@user_router.callback_query(F.data.startswith("stickers:pick:"))
async def cb_pick_pack(call: CallbackQuery, state: FSMContext):
    idx = int(call.data.split(":")[-1])
    packs = get_user_packs(call.from_user.id)

    if idx < 0 or idx >= len(packs):
        await call.answer("Пак не найден. Обнови список.", show_alert=True)
        return

    pack_name = packs[idx]
    await state.update_data(pack_name=pack_name)
    await state.set_state(AddStickerFSM.STREAM)

    await call.message.answer(
        f"Пак выбран: {pack_name}\nТеперь отправляй стикеры или картинки.",
        reply_markup=pack_open_kb(pack_name)
    )
    await call.answer()
