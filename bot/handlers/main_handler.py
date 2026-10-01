from time import time
from typing import Any

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.buttons.reply import reply_button_builder
from bot.states import RegisterState
from db.models import User

router = Router()
COOLDOWN_SECONDS = 300


@router.message(CommandStart())
async def handle_start(message: Message, state: FSMContext):
    user: User | None = await User.get(user_id=message.chat.id)
    if user and user.is_admin:
        buttons: list[str] = ["📃 Reports", "📊 Statistic", "📃 My Accept Reports"]
        markup = reply_button_builder(buttons, (2,))
        await message.answer(text="Hush kelibsiz", reply_markup=markup)
        return
    await state.set_state(RegisterState.game_username)
    await message.answer(text="CS2 dagi usernameingizni yozing")


@router.message(RegisterState.game_username)
@router.message(F.text == "⬅️ Back")
async def handle_game_username(message: Message, state: FSMContext):
    data: dict = await state.get_data()
    current_time = time()
    stored_reporter_id = data.get("reporter_id")
    last_reported_at = data.get("last_reported_at")

    if stored_reporter_id == message.chat.id and last_reported_at:
        elapsed = current_time - last_reported_at
        if elapsed < COOLDOWN_SECONDS:
            remaining_minutes = int((COOLDOWN_SECONDS - elapsed) // 60) + 1
            await message.answer(
                f"Siz allaqachon ariza qoldirgansiz! "
                f"Yangi arizani {remaining_minutes} daqiqadan so'ng qoldirishingiz mumkin."
            )
            return

    if message.text != "⬅️ Back":
        user_data: dict[str, Any] = {
            "user_id": message.chat.id,
            "username": message.chat.username,
            "game_username": message.text
        }
        await User.check_user(data=user_data)

    buttons: list[str] = ["🟡 Steam ID", "🟠 Game username", "📃 Reports"]
    markup = reply_button_builder(buttons, (2, 1))
    await message.answer(text="Qoidabuzarning ma'lumotini kiriting:", reply_markup=markup)
    await state.set_state(None)
    if last_reported_at:
        await state.set_data({
            "reporter_id": message.chat.id,
            "last_reported_at": last_reported_at
        })