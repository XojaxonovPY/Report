from typing import Any

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.buttons.middleware import MediaGroupMiddleware
from bot.states import EvidenceState
from db.models import Report, Buller

router = Router()

router.message.middleware(MediaGroupMiddleware())


@router.message(F.text == "📷 Photo")
async def photo_button_handler(message: Message, state: FSMContext):
    await state.set_state(EvidenceState.photo)
    await message.answer(text="Screenshotni yuboring")


@router.message(F.text == "📹 Video")
async def video_button_handler(message: Message, state: FSMContext):
    await state.set_state(EvidenceState.video)
    await message.answer(text="Olingan videoni yuboring")


@router.message(F.text == "🎙 Audio")
async def audio_button_handler(message: Message, state: FSMContext):
    await state.set_state(EvidenceState.audio)
    await message.answer(text="Olingan audioni yuboring")


@router.message(F.text == "🔗 Link")
async def link_button_handler(message: Message, state: FSMContext):
    await state.set_state(EvidenceState.link)
    await message.answer(text="Demo linki yuboring")


async def report_creator(message: Message, data: dict[str, Any], reporter_data: dict[str, Any]):
    buller_data: dict[str, int | str] = {}
    if data.get("steam_id"):
        buller_data['steam_id'] = data["steam_id"]
    elif data.get("game_username"):
        buller_data['game_username'] = data["game_username"]
    buller: Buller | None = await Buller.get(**buller_data)
    if not buller:
        buller = await Buller.create(**buller_data)
    else:
        await Buller.update(filter_=buller_data, report_count=buller.report_count + 1)
    reporter_data["buller_id"] = buller.id
    if data.get("comment"):
        reporter_data['comment'] = data["comment"]
    elif data.get("reason_id"):
        reporter_data['reason_id'] = data["reason_id"]
    await Report.create(**reporter_data)
    await message.answer(text="Arizangiz qabul qilindi")


@router.message(EvidenceState.photo, F.photo)
async def photo_handler(message: Message, state: FSMContext, album: list[Message] = None):
    if album:
        photo_ids = [msg.photo[-1].file_id for msg in album]
    else:
        photo_ids = [message.photo[-1].file_id]
    data = await state.get_data()
    reporter_data = {'reporter_id': message.chat.id, "evidence": {"photos": photo_ids}}
    await report_creator(message, data, reporter_data)


@router.message(EvidenceState.video, F.video)
async def video_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    reporter_data = {'reporter_id': message.chat.id, "evidence": {"video": message.video.file_id}}
    await report_creator(message, data, reporter_data)


@router.message(EvidenceState.audio, F.audio)
async def audio_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    reporter_data = {'reporter_id': message.chat.id, "evidence": {"audio": message.audio.file_id}}
    await report_creator(message, data, reporter_data)


@router.message(EvidenceState.link)
async def link_handler(message: Message, state: FSMContext):
    url: str = message.text
    if not url.startswith("https://"):
        await message.answer(text="Incorrect link")
    data = await state.get_data()
    reporter_data = {'reporter_id': message.chat.id, "evidence": {"link": url}}
    await report_creator(message, data, reporter_data)
