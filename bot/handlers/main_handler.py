from typing import Any

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.buttons.reply import reply_button_builder
from bot.states import RegisterState
from db.models import User

router = Router()


@router.message(CommandStart())
async def handle_start(message: Message, state: FSMContext):
    user: User | None = await User.get(user_id=message.chat.id)
    if user and user.is_admin:
        buttons: list[str] = ["📃 Reports", "📊 Statistic", "📃 My Accept Reports"]
        markup = reply_button_builder(buttons, (2,))
        await message.answer(text="Hush kelibsiz", reply_markup=markup)
        return
    await state.set_state(RegisterState.gama_username)
    await message.answer(text="CS2 dagi usernameingizni yozing")


@router.message(RegisterState.gama_username)
@router.message(F.text == "⬅️ Back")
async def handle_game_username(message: Message, state: FSMContext):
    game_username: str = message.text
    user_data: dict[str, Any] = {
        "user_id": message.chat.id,
        "username": message.chat.username,
        "game_username": game_username
    }
    await User.check_user(data=user_data)
    buttons: list[str] = ["🟡 Steam ID", "🟠 Game username", "📃 Reports"]
    markup = reply_button_builder(buttons, (2,))
    await message.answer(text="Qoida buzarni malumotini kiriting", reply_markup=markup)
    await state.clear()
