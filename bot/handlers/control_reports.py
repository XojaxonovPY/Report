import asyncio

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.utils.media_group import MediaGroupBuilder

from bot.buttons.inline import inline_button_builder
from bot.states import RejectState
from db.enum import ReportStatus
from db.models import User, Report

router = Router()


def format_report_text(report: Report, include_admin: bool = False) -> str:
    """Arizalar uchun umumiy formatlangan matn (caption) tayyorlash."""
    buller: str | int = "Noma'lum"
    if report.buller:
        buller = report.buller.steam_id if report.buller.steam_id else (report.buller.game_username or "Noma'lum")

    reason: str = report.reason.text if (report.reason_id and report.reason) else (report.comment or "Ko'rsatilmagan")

    reporter_username = f"@{report.reporter.username}" if (report.reporter and report.reporter.username) else "Mavjud emas"
    gamer_nickname = report.reporter.game_username if report.reporter else "Noma'lum"
    status_val = report.status.value if hasattr(report.status, "value") else str(report.status)
    status_str = f"#{status_val.replace(' ', '_')}"

    text = (
        f"<b>Report ID:</b> #{report.id}\n"
        f"<b>Reporter telegram username:</b> {reporter_username}\n"
        f"<b>Gamer nickname:</b> {gamer_nickname}\n"
        f"<b>Buller:</b> {buller}\n"
        f"<b>Reason:</b> {reason}\n"
        f"<b>Status:</b> {status_str}"
    )

    if include_admin:
        if report.assigned_admin_id and report.admin and report.admin.username:
            admin_name = f"@{report.admin.username}"
        elif report.assigned_admin_id:
            admin_name = f"ID: {report.assigned_admin_id}"
        else:
            admin_name = "Free"
        text += f"\n<b>Assigment admin:</b> {admin_name}"

    return text


def build_report_actions_markup(admin_id: int | str, report_id: int | str, action_type: str = "pending") -> InlineKeyboardMarkup:
    """Admin harakatlari uchun inline tugmalar yaratish."""
    if action_type == "pending":
        first_btn = InlineKeyboardButton(text="Qabul qilish", callback_data=f"accept_{admin_id}_{report_id}")
    else:  # in_progress
        first_btn = InlineKeyboardButton(text="Yakunlash", callback_data=f"finish_{admin_id}_{report_id}")

    reject_btn = InlineKeyboardButton(text="Rad Etish", callback_data=f"reject_{admin_id}_{report_id}")
    return inline_button_builder([first_btn, reject_btn], (2,))


async def send_report_card(
    message: Message,
    report: Report,
    include_admin: bool = False,
    reply_markup: InlineKeyboardMarkup | None = None,
) -> None:
    """Arizani dalillari (rasm, video, audio, havola) va tugmalari bilan yuborish."""
    text = format_report_text(report, include_admin=include_admin)

    match report.evidence:
        case {"photos": photos} if photos:
            album_builder = MediaGroupBuilder(caption=text)
            for file_id in photos:
                album_builder.add_photo(media=file_id)
            await message.answer_media_group(media=album_builder.build())
            if reply_markup:
                await message.answer("Qaror qabul qiling:", reply_markup=reply_markup)

        case {"video": video}:
            await message.answer_video(video=video, caption=text, reply_markup=reply_markup)

        case {"audio": audio}:
            await message.answer_audio(audio=audio, caption=text, reply_markup=reply_markup)

        case {"link": link}:
            await message.answer(text=f"{link}\n\n{text}", reply_markup=reply_markup)

        case _:
            await message.answer(text=text, reply_markup=reply_markup)


@router.message(F.text == "📃 Reports")
async def reports_handler(message: Message):
    user_id: int = message.chat.id
    is_admin, admin = await User.check_admin(user_id)

    if is_admin:
        reports = await Report.get_filter(
            Report.status == ReportStatus.PENDING.value,
            Report.assigned_admin_id == None,
            order_by_fields=[Report.created_at.asc()]
        )
        if not reports:
            await message.answer(text="Hozirda arizalar mavjud emas)")
            return

        for report in reports:
            markup = build_report_actions_markup(admin.user_id, report.id, action_type="pending")
            await send_report_card(message, report, include_admin=False, reply_markup=markup)
            await asyncio.sleep(0.3)
    else:
        reports = await Report.get_filter(
            Report.reporter_id == admin.user_id,
            order_by_fields=[Report.created_at.asc()]
        )
        if not reports:
            await message.answer(text="Sizda hali arizalar mavjud emas.")
            return

        for report in reports:
            await send_report_card(message, report, include_admin=True)
            await asyncio.sleep(0.5)


@router.callback_query(F.data.startswith("accept_"))
async def accept_button(callback: CallbackQuery):
    _, admin_id, report_id = callback.data.split("_")
    await Report.update(filter_={"id": report_id}, status=ReportStatus.IN_PROGRESS.value, assigned_admin_id=admin_id)
    report = await Report.get(id=report_id)

    if not report:
        await callback.answer(text="Ariza topilmadi!")
        return

    markup = build_report_actions_markup(admin_id, report.id, action_type="in_progress")
    await send_report_card(callback.message, report, include_admin=True, reply_markup=markup)
    await callback.answer()


@router.callback_query(F.data.startswith("finish_"))
async def finish_button(callback: CallbackQuery, bot: Bot):
    _, admin_id, report_id = callback.data.split("_")
    report: Report = await Report.update(filter_={"id": report_id}, status=ReportStatus.ACCEPTANCE.value)
    user: User = await User.get(user_id=admin_id)
    if user:
        await User.update(filter_={"user_id": user.user_id}, report_checks=user.report_checks + 1)

    text: str = f"Sizning #{report.id} idli arizangiz admin tarafidan qabul qilindi"
    await bot.send_message(report.reporter_id, text=text)
    await callback.message.answer(text="Ariza yakunlandi")
    await callback.answer()


@router.callback_query(F.data.startswith("reject_"))
async def reject_button(callback: CallbackQuery, state: FSMContext):
    _, admin_id, report_id = callback.data.split("_")
    await state.update_data(admin_id=admin_id, report_id=report_id)
    await state.set_state(RejectState.reason)
    await callback.message.answer(text="Rad etilishi uchun sabab yozing")
    await callback.answer()


@router.message(RejectState.reason)
async def reject_reason_handler(message: Message, state: FSMContext, bot: Bot):
    reason_reject = message.text
    data = await state.get_data()
    report_id = data.get("report_id")

    report: Report = await Report.update(
        filter_={"id": report_id}, status=ReportStatus.REJECTED.value, reason_rejected=reason_reject
    )
    text: str = f"Sizning #{report.id} idli arizangiz admin tarafidan rad etildi\nSababi: {reason_reject}"
    await bot.send_message(report.reporter_id, text=text)
    await message.answer(text="Ariza yakunlandi")
    await state.clear()


@router.message(F.text == "📃 My Accept Reports")
async def get_admin_accept_reports(message: Message):
    reports: list[Report] = await Report.get_filter(
        Report.assigned_admin_id == message.chat.id,
        Report.status.in_((ReportStatus.ACCEPTANCE.value, ReportStatus.IN_PROGRESS.value)),
        order_by_fields=[Report.created_at.desc()]
    )
    if not reports:
        await message.answer(text="Sizda qabul qilingan arizalar mavjud emas)")
        return

    for report in reports:
        await send_report_card(message, report, include_admin=False)
        await asyncio.sleep(0.3)
