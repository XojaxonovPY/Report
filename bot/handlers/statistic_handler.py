import asyncio

from aiogram import Router, F
from aiogram.types import Message
from sqlalchemy import select

from db.models import User, Buller

router = Router()


@router.message(F.text == "📊 Statistic")
async def get_statistic(message: Message):
    active_admins_stmt = (
        select(User.username, User.report_checks)
        .where(User.is_admin == True)
        .select_from(User)
        .order_by(User.report_checks.desc())
    )
    active_buller_stmt = (
        select(Buller.game_username, Buller.steam_id, Buller.report_count)
        .select_from(Buller)
        .order_by(Buller.report_count.desc())
    )
    active_admins_data = await User.query(active_admins_stmt)
    active_buller_data = await Buller.query(active_buller_stmt)
    for admins in active_admins_data.mappings().all():
        text = f"<b>Admin:</b>{admins.get("username")}\n<b>Reports count:</b>{admins.get("report_checks")}"
        await message.answer(text=text)
        await asyncio.sleep(2)
    for bullers in active_buller_data.mappings().all():
        if bullers.get("steam_id"):
            buller_address = f"<b>Steam_ID:</b>{bullers.get("steam_id")}"
        else:
            buller_address = f"<b>Game Username:</b>{bullers.get("game_username")}"
        text = f"{buller_address}\n<b>Report Count:</b>{bullers.report_count}"
        await message.answer(text=text)
        await asyncio.sleep(2)
