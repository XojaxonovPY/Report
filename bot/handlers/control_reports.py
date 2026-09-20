import asyncio

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery
from aiogram.utils.media_group import MediaGroupBuilder

from bot.buttons.inline import inline_button_builder
from bot.states import RejectState
from db.enum import ReportStatus
from db.models import User, Report

router = Router()


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
        for report in reports:
            buller: str | int = report.buller.steam_id if report.buller.steam_id else report.buller.game_username
            reason: str = report.reason.text if report.reason_id else report.comment
            text: str = (
                f"<b>Report ID:</b>{report.id}\n"
                f"<b>Reporter telegram username:</b>@{report.reporter.username}\n"
                f"<b>Gamer nickname:</b>{report.reporter.game_username}\n"
                f"<b>Buller:</b>{buller}\n"
                f"<b>Reason:</b>{reason}\n"
                f"<b>Status:</b>#{report.status.value}"
            )
            buttons: list[InlineKeyboardButton] = [
                InlineKeyboardButton(text="Qabul qilish", callback_data=f"accept_{admin.id}_{report.id}"),
                InlineKeyboardButton(text="Rad Etish", callback_data=f"reject_{admin.id}_{report.id}")
            ]
            markup = inline_button_builder(buttons, (2,))
            match report.evidence:
                case {"photos": photos}:
                    album_builder = MediaGroupBuilder(caption=text)
                    for file_id in photos:
                        album_builder.add_photo(media=file_id)

                    await message.answer_media_group(media=album_builder.build())
                    await message.answer("Qaror qabul qiling:", reply_markup=markup)

                case {"video": video}:
                    await message.answer_video(video=video, caption=text, reply_markup=markup)

                case {"audio": audio}:
                    await message.answer_audio(audio=audio, caption=text, reply_markup=markup)

                case {"link": link}:
                    await message.answer(text=f"{link}\n{text}", reply_markup=markup)

    else:
        reports = await Report.get_filter(
            Report.reporter_id == admin.user_id,
            order_by_fields=[Report.created_at.asc()]
        )
        for report in reports:
            buller: str | int = report.buller.steam_id if report.buller.steam_id else report.buller.game_username
            reason: str = report.reason.text if report.reason_id else report.comment
            assigment_admin = report.admin.username if report.assigned_admin_id else "Free"
            text: str = (
                f"<b>Report ID:</b>{report.id}\n"
                f"<b>Reporter telegram username:</b>{report.reporter.username}\n"
                f"<b>Gamer nickname:</b> {report.reporter.game_username}\n"
                f"<b>Buller:</b>{buller}\n"
                f"<b>Reason:</b>{reason}\n"
                f"<b>Status:</b>#{report.status.value}\n"
                f"<b>Assigment admin:</b>{assigment_admin}"
            )
            match report.evidence:
                case {"photos": photos}:
                    album_builder = MediaGroupBuilder(caption=text)
                    for file_id in photos:
                        album_builder.add_photo(media=file_id)
                    await message.answer_media_group(media=album_builder.build())
                case {"video": video}:
                    await message.answer_video(video=video, caption=text)
                case {"audio": audio}:
                    await message.answer_audio(audio=audio, caption=text)
                case {"link": link}:
                    await message.answer(text=f"{link}\n{text}")
            await asyncio.sleep(0.5)


@router.callback_query(F.data.startswith("accept_"))
async def accept_button(callback: CallbackQuery):
    admin_id, report_id = callback.data.split("_")[1], callback.data.split("_")[2]
    report = await Report.update(filter_={"id": report_id}, status=ReportStatus.IN_PROGRESS.value,
                                 assigned_admin_id=admin_id)
    buttons: list[InlineKeyboardButton] = [
        InlineKeyboardButton(text="Qabul qilish", callback_data=f"finish_{admin_id}_{report.id}"),
        InlineKeyboardButton(text="Rad Etish", callback_data=f"reject_{admin_id}_{report.id}")
    ]
    markup = inline_button_builder(buttons, (2,))
    buller: str | int = report.buller.steam_id if report.buller.steam_id else report.buller.game_username
    reason: str = report.reason.text if report.reason_id else report.comment
    assigment_admin = report.admin.username if report.assigned_admin_id else "Free"
    text: str = (
        f"<b>Report ID:</b>{report.id}\n"
        f"<b>Reporter telegram username:</b>{report.reporter.username}\n"
        f"<b>Gamer nickname:</b> {report.reporter.game_username}\n"
        f"<b>Buller:</b>{buller}\n"
        f"<b>Reason:</b>{reason}\n"
        f"<b>Status:</b>#{report.status.value}\n"
        f"<b>Assigment admin:</b>{assigment_admin}"
    )
    match report.evidence:
        case {"photos": photos}:
            album_builder = MediaGroupBuilder(caption=text)
            for file_id in photos:
                album_builder.add_photo(media=file_id)

            await callback.message.answer_media_group(media=album_builder.build())
            await callback.message.answer("Qaror qabul qiling:", reply_markup=markup)

        case {"video": video}:
            await callback.message.answer_video(video=video, caption=text, reply_markup=markup)

        case {"audio": audio}:
            await callback.message.answer_audio(audio=audio, caption=text, reply_markup=markup)

        case {"link": link}:
            await callback.message.answer(text=f"{link}\n{text}", reply_markup=markup)


@router.callback_query(F.data.startswith("finish_"))
async def finish_button(callback: CallbackQuery, bot: Bot):
    admin_id, report_id = callback.data.split("_")[1], callback.data.split("_")[2]
    report: Report = await Report.update(filter_={"id": report_id}, status=ReportStatus.ACCEPTANCE.value)
    user: User = await User.get(user_id=admin_id)
    await User.update(filter_={"user_id": user.user_id}, report_checks=user.report_checks + 1)
    await bot.send_message(report.reporter_id, text=f"Sizning {report.id} idli arizangiz admin tarafidan qabul qilindi")
    await callback.message.answer(text="Ariza yakunlandi")


@router.callback_query(F.data.startswith("reject_"))
async def reject_button(callback: CallbackQuery, state: FSMContext):
    admin_id, report_id = callback.data.split("_")[1], callback.data.split("_")[2]
    await state.update_data(admin_id=admin_id, report_id=report_id)
    await state.set_state(RejectState.reason)
    await callback.message.answer(text="Rad etilishi uchun sabab yozing")


@router.message(RejectState.reason)
async def reject_reason_handler(message: Message, state: FSMContext, bot: Bot):
    reason_reject = message.text
    data = await state.get_data()
    admin_id, report_id = data.get("admin_id"), data.get("report_id")
    report: Report = await Report.update(
        filter_={"id": report_id}, status=ReportStatus.REJECTED.value, reason_rejected=reason_reject
    )
    await bot.send_message(report.reporter_id, text=f"Sizning {report.id} idli admin tarafidan rad etildi")
    await message.answer(text="Ariza yakunlandi")
