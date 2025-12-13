from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from bot.fsm.add_sticker import AddStickerFSM

router = Router()

# Команда /add_stickers
@router.message(Command("add_stickers"))
async def add_stickers_cmd(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(AddStickerFSM.WAIT_PACK)
    await message.answer(
        "Пришли short_name стикерпака\n"
        "Пример: my_pack_by_bot"
    )

# Handler ввода short_name пака
@router.message(AddStickerFSM.WAIT_PACK)
async def set_pack_name(message: Message, state: FSMContext):
    pack_name = message.text.strip()
    await state.update_data(pack_name=pack_name)
    await state.set_state(AddStickerFSM.STREAM)
    await message.answer(
        f"Пак `{pack_name}` выбран.\n"
        "Теперь отправляй стикеры или картинки."
    )

# STREAM handler заглушка
@router.message(AddStickerFSM.STREAM)
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
