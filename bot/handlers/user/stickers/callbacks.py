import logging

from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.fsm.add_sticker import AddStickerFSM
from bot.handlers.user.start import send_start_menu
from bot.handlers.user.stickers.keyboards import packs_select_kb, pack_open_kb
from storage.google_sheets import get_user_packs

from bot.handlers.user.constants import (
    CB_STICKERS_CREATE,
    CB_STICKERS_EDIT,
    CB_STICKERS_STOP_EDIT,
    CB_STICKERS_PICK_PREFIX,
    TEXT_STOPPED,
)

# НАПИСАТЬ ЛОГИ
logger = logging.getLogger("bot")

router = Router()

@router.callback_query(F.data == CB_STICKERS_STOP_EDIT)
async def cb_stop_edit(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.answer(TEXT_STOPPED)
    await send_start_menu(call.message)
    await call.answer()

@router.callback_query(F.data == CB_STICKERS_EDIT)
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

@router.callback_query(F.data == CB_STICKERS_CREATE)
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

@router.callback_query(F.data.startswith(CB_STICKERS_PICK_PREFIX))
async def cb_pick_pack(call: CallbackQuery, state: FSMContext):
    # CB_STICKERS_PICK_PREFIX = "stickers:pick:"
    suffix = call.data[len(CB_STICKERS_PICK_PREFIX):]
    try:
        idx = int(suffix)
    except ValueError:
        await call.answer("Некорректный выбор.", show_alert=True)
        return

    packs = get_user_packs(call.from_user.id)
    if idx < 0 or idx >= len(packs):
        await call.answer("Пак не найден. Обнови список.", show_alert=True)
        return

    pack_name = packs[idx]
    await state.update_data(pack_name=pack_name)
    await state.set_state(AddStickerFSM.STREAM)

    await call.message.answer(
        f"Пак выбран: {pack_name}\nТеперь отправляй стикеры или картинки.",
        reply_markup=pack_open_kb(pack_name),
    )
    await call.answer()