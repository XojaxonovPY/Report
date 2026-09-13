from sqlalchemy import update
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from starlette_admin import ActionSelection, action, flash
from starlette_admin.contrib.sqla import Admin, ModelView

from admin.provider import UsernameAndPasswordProvider
from db import engine
from db.enum import ReportStatus
from db.models import Buller, Reason, Report, User
from db.session import AsyncSessionLocal


class UserAdmin(ModelView):
    name = "Foydalanuvchilar"
    label = "Foydalanuvchilar"
    icon = "fa-solid fa-users"
    searchable_fields = [User.user_id, User.username, User.game_username]
    sortable_fields = [
        User.user_id,
        User.username,
        User.game_username,
        User.is_admin,
        User.report_checks,
        User.last_report,
        User.created_at,
    ]
    fields_default_sort = [(User.created_at, True)]
    page_size = 25
    page_size_options = [10, 25, 50, 100]
    exclude_fields_from_create = [User.created_at]
    exclude_fields_from_edit = [User.created_at]
    actions = ["make_admin", "revoke_admin"]

    @action(
        name="make_admin",
        text="Admin qilish",
        confirmation="Tanlangan foydalanuvchilarga admin huquqini berishni tasdiqlaysizmi?",
        submit_btn_class="btn btn-success",
        icon_class="fa-solid fa-user-shield",
    )
    async def make_admin(self, request: Request, selection: ActionSelection) -> None:
        pks = await selection.pks()
        async with AsyncSessionLocal() as session:
            stmt = (
                update(User)
                .where(User.user_id.in_([int(pk) for pk in pks]))
                .values(is_admin=True)
            )
            await session.execute(stmt)
            await session.commit()
        flash(
            request, f"{len(pks)} ta foydalanuvchiga admin huquqi berildi.", "success"
        )

    @action(
        name="revoke_admin",
        text="Adminlikni olib tashlash",
        confirmation="Tanlangan foydalanuvchilarning admin huquqini olib tashlashni tasdiqlaysizmi?",
        submit_btn_class="btn btn-danger",
        icon_class="fa-solid fa-user-xmark",
    )
    async def revoke_admin(self, request: Request, selection: ActionSelection) -> None:
        pks = await selection.pks()
        async with AsyncSessionLocal() as session:
            stmt = (
                update(User)
                .where(User.user_id.in_([int(pk) for pk in pks]))
                .values(is_admin=False)
            )
            await session.execute(stmt)
            await session.commit()
        flash(
            request, f"{len(pks)} ta foydalanuvchidan admin huquqi olindi.", "info"
        )


class ReportAdmin(ModelView):
    name = "Shikoyatlar"
    label = "Shikoyatlar"
    icon = "fa-solid fa-triangle-exclamation"
    searchable_fields = [Report.id, Report.comment, Report.reason_rejected]
    sortable_fields = [
        Report.id,
        Report.status,
        Report.updated_at,
        Report.created_at,
    ]
    fields_default_sort = [(Report.created_at, True)]
    page_size = 20
    page_size_options = [10, 20, 50, 100]
    exclude_fields_from_create = [Report.created_at, Report.updated_at]
    exclude_fields_from_edit = [Report.created_at, Report.updated_at]
    actions = ["accept_reports", "reject_reports", "in_progress_reports"]

    @action(
        name="accept_reports",
        text="Qabul qilish (Accept)",
        confirmation="Tanlangan shikoyatlarni qabul qilindi deb belgilashni tasdiqlaysizmi?",
        submit_btn_class="btn btn-success",
        icon_class="fa-solid fa-check",
    )
    async def accept_reports(
        self, request: Request, selection: ActionSelection
    ) -> None:
        pks = await selection.pks()
        async with AsyncSessionLocal() as session:
            stmt = (
                update(Report)
                .where(Report.id.in_([int(pk) for pk in pks]))
                .values(status=ReportStatus.ACCEPTANCE.value)
            )
            await session.execute(stmt)
            await session.commit()
        flash(request, f"{len(pks)} ta shikoyat qabul qilindi.", "success")

    @action(
        name="reject_reports",
        text="Rad etish (Reject)",
        confirmation="Tanlangan shikoyatlarni rad etildi deb belgilashni tasdiqlaysizmi?",
        submit_btn_class="btn btn-danger",
        icon_class="fa-solid fa-xmark",
    )
    async def reject_reports(
        self, request: Request, selection: ActionSelection
    ) -> None:
        pks = await selection.pks()
        async with AsyncSessionLocal() as session:
            stmt = (
                update(Report)
                .where(Report.id.in_([int(pk) for pk in pks]))
                .values(status=ReportStatus.REJECTED.value)
            )
            await session.execute(stmt)
            await session.commit()
        flash(request, f"{len(pks)} ta shikoyat rad etildi.", "warning")

    @action(
        name="in_progress_reports",
        text="Jarayonda (In Progress)",
        confirmation="Tanlangan shikoyatlarni jarayonda deb belgilashni tasdiqlaysizmi?",
        submit_btn_class="btn btn-warning",
        icon_class="fa-solid fa-spinner",
    )
    async def in_progress_reports(
        self, request: Request, selection: ActionSelection
    ) -> None:
        pks = await selection.pks()
        async with AsyncSessionLocal() as session:
            stmt = (
                update(Report)
                .where(Report.id.in_([int(pk) for pk in pks]))
                .values(status=ReportStatus.IN_PROGRESS.value)
            )
            await session.execute(stmt)
            await session.commit()
        flash(request, f"{len(pks)} ta shikoyat jarayonga o'tkazildi.", "info")


class BullerAdmin(ModelView):
    name = "Qoida buzarlar"
    label = "Qoida buzarlar"
    icon = "fa-solid fa-user-slash"
    searchable_fields = [Buller.game_username, Buller.steam_id]
    sortable_fields = [
        Buller.id,
        Buller.game_username,
        Buller.steam_id,
        Buller.report_count,
        Buller.created_at,
    ]
    fields_default_sort = [(Buller.report_count, True)]
    page_size = 25
    page_size_options = [10, 25, 50, 100]
    exclude_fields_from_create = [Buller.created_at]
    exclude_fields_from_edit = [Buller.created_at]


class ReasonAdmin(ModelView):
    name = "Shikoyat sabablari"
    label = "Shikoyat sabablari"
    icon = "fa-solid fa-list-check"
    searchable_fields = [Reason.text]
    sortable_fields = [Reason.id, Reason.text, Reason.created_at]
    fields_default_sort = [(Reason.id, False)]
    page_size = 20
    page_size_options = [10, 20, 50]
    exclude_fields_from_create = [Reason.created_at]
    exclude_fields_from_edit = [Reason.created_at]


app = Starlette()
admin = Admin(
    engine,
    title="ReportBot Admin",
    base_url="/",
    secret_key="sdgfhjhhsfdghn",
    auth_provider=UsernameAndPasswordProvider(),
    middlewares=[Middleware(SessionMiddleware, secret_key="sdgfhjhhsfdghn")],
)

admin.add_view(UserAdmin(User))
admin.add_view(ReportAdmin(Report))
admin.add_view(BullerAdmin(Buller))
admin.add_view(ReasonAdmin(Reason))

admin.mount_to(app)
