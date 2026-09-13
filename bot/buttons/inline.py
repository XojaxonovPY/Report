from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def inline_button_builder(buttons: list[InlineKeyboardButton], size=(1,)) -> InlineKeyboardMarkup:
    ikb = InlineKeyboardBuilder()
    ikb.add(*buttons)
    ikb.adjust(*size)
    return ikb.as_markup()
