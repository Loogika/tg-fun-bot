from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.handlers.user.constants import (
    BTN_OPEN_PACK,
    BTN_STOP_EDIT,
    CB_STICKERS_STOP_EDIT,
    CB_STICKERS_PICK_PREFIX,
    MAX_PACK_BUTTONS,
)

def pack_open_kb(pack_name: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=BTN_OPEN_PACK, url=f"https://t.me/addstickers/{pack_name}")
    kb.adjust(1)
    return kb.as_markup()

def stream_kb(pack_name: str | None = None) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    if pack_name:
        kb.button(text=BTN_OPEN_PACK, url=f"https://t.me/addstickers/{pack_name}")
    kb.button(text=BTN_STOP_EDIT, callback_data=CB_STICKERS_STOP_EDIT)
    kb.adjust(1)
    return kb.as_markup()

def packs_select_kb(packs: list[str]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for i, name in enumerate(packs[:MAX_PACK_BUTTONS]):
        kb.button(text=name, callback_data=f"{CB_STICKERS_PICK_PREFIX}{i}")
    kb.adjust(1)
    return kb.as_markup()
