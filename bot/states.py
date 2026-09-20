from aiogram.fsm.state import StatesGroup, State


class States(StatesGroup):
    lang = State()


class RegisterState(StatesGroup):
    gama_username = State()


class AcceptState(StatesGroup):
    steam_id = State()
    game_username = State()
    comment = State()


class EvidenceState(StatesGroup):
    photo = State()
    video = State()
    audio = State()
    link = State()


class RejectState(StatesGroup):
    reason = State()
