import logging

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery

from bot.buttons.inline import inline_button_builder
from bot.buttons.reply import reply_button_builder
from bot.states import AcceptState
from db.models import Reason

router = Router()


@router.message(F.text == "🟡 Steam ID")
async def steam_id_handler(message: Message, state: FSMContext):
    await state.set_state(AcceptState.steam_id)
    await message.answer(text="Steam ID ni yuboring")


@router.message(F.text == "🟠 Game username")
async def game_username_handler(message: Message, state: FSMContext):
    await state.set_state(AcceptState.game_username)
    await message.answer(text="Game username ni yuboring")


@router.message(StateFilter(AcceptState.steam_id, AcceptState.game_username))
async def buller_handler(message: Message, state: FSMContext):
    curren_state = await state.get_state()
    buller_address: str = message.text
    buller_data: dict[str, str | int] = {}
    if curren_state == AcceptState.steam_id.state:
        try:
            buller_data["steam_id"] = int(buller_address)
        except ValueError as e:
            logging.error(e)
            await message.answer(text="Steam Id notog'ri kiritilgan")
            return
    elif curren_state == AcceptState.game_username.state:
        buller_data["game_username"] = buller_address
    await state.update_data(**buller_data)
    buttons: list[InlineKeyboardButton] = [
        InlineKeyboardButton(text=reason.text, callback_data=f"reason_{reason.id}")
        async for reason in Reason.stream_all()
    ]
    buttons.append(InlineKeyboardButton(text="Another ➡️", callback_data="another"))
    markup = inline_button_builder(buttons, [2] * (len(buttons) // 2))
    await message.answer(text="O'zingizga togri keladigan sabablardan birini tanlang:", reply_markup=markup)


@router.callback_query(F.data == "another")
async def another_handler(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AcceptState.comment)
    await callback.message.answer(text="Sababni toliqroq qilib yozing")


async def evidence_buttons(message: Message):
    buttons: list[str] = ["📷 Photo", "📹 Video", "🎙 Audio", "🔗 Link", "⬅️ Back"]
    markup = reply_button_builder(buttons, (2, 2))
    await message.answer(text="Manashulardan birini tanlab dalilngizni yuboring", reply_markup=markup)


@router.message(AcceptState.comment)
async def comment_handler(message: Message, state: FSMContext):
    await state.update_data(comment=message.text)
    await state.set_state(None)
    await evidence_buttons(message)


@router.callback_query(F.data.startswith("reason_"))
async def reason_handler(callback: CallbackQuery, state: FSMContext):
    await state.update_data(reason_id=int(callback.data.split("_")[1]))
    await state.set_state(None)
    await evidence_buttons(callback.message)
