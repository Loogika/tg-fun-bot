from aiogram.fsm.state import StatesGroup, State

class AddStickerFSM(StatesGroup):
    WAIT_PACK = State()
    STREAM = State()
