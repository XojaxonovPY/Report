from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, ReplyKeyboardMarkup


def reply_button_builder(text: list[str], size=(1,), one_time=False) -> ReplyKeyboardMarkup:
    rkb = ReplyKeyboardBuilder()
    rkb.add(*[KeyboardButton(text=i) for i in text])
    rkb.adjust(*size)
    return rkb.as_markup(resize_keyboard=True, one_time_keyboard=one_time)
