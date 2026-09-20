from datetime import datetime
from typing import Any

from sqlalchemy import String, BIGINT, Boolean, Integer, TEXT, ForeignKey, Enum, DateTime, func, JSON
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.enum import ReportStatus
from db.exceptions import DatabaseException, logger
from db.utils import Base
from db.utils import Model


class User(Model):
    id = None
    user_id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(length=100), nullable=True)
    game_username: Mapped[str] = mapped_column(String(length=100), nullable=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    report_checks: Mapped[int] = mapped_column(Integer, default=0)
    last_report: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    reports_sent: Mapped[list["Report"]] = relationship(
        "Report", back_populates="reporter", foreign_keys="Report.reporter_id", lazy="selectin"
    )
    reports_handled: Mapped[list["Report"]] = relationship(
        "Report", back_populates="admin", foreign_keys="Report.assigned_admin_id", lazy="selectin"
    )

    @staticmethod
    async def check_user(data: dict):
        query: User | None = await User.get(user_id=data.get('user_id'))
        if not query:
            try:
                await User.create(**data)
            except DatabaseException as e:
                logger.error(msg=e)
        else:
            try:
                if data["game_username"] != query.game_username:
                    await User.update(filter_={"user_id": query.user_id}, game_username=data.get('game_username'))
            except DatabaseException as e:
                logger.error(msg=e)

    @staticmethod
    async def check_admin(user_id: int):
        user: User | None = await User.get(user_id=user_id)
        if user and user.is_admin:
            return True, user
        else:
            return False, user

    def __str__(self):
        return self.username or f"User #{self.user_id}"


class Reason(Model):
    text: Mapped[str] = mapped_column(String(length=300), nullable=True)
    reports: Mapped[list["Report"]] = relationship("Report", back_populates="reason", lazy="selectin")

    def __str__(self):
        return self.text or f"Reason #{self.id}"


values_callable = lambda obj: [e.value for e in obj]


class Buller(Model):
    game_username: Mapped[str] = mapped_column(String(length=100), index=True, nullable=True)
    steam_id: Mapped[int] = mapped_column(BIGINT, index=True, nullable=True)
    report_count: Mapped[int] = mapped_column(Integer, default=1)
    reports: Mapped[list["Report"]] = relationship("Report", back_populates="buller", lazy="selectin")

    def __str__(self):
        name = self.game_username or "No Username"
        steam = f" (Steam: {self.steam_id})" if self.steam_id else ""
        return f"{name}{steam}"


class Report(Model):
    reporter_id: Mapped[int] = mapped_column(ForeignKey(column="users.user_id", ondelete="CASCADE"), index=True)
    evidence: Mapped[dict[str, Any]] = mapped_column(MutableDict.as_mutable(JSON), default=dict, nullable=True)
    buller_id: Mapped[int] = mapped_column(ForeignKey(column="bullers.id", ondelete="SET NULL"))
    reason_id: Mapped[int] = mapped_column(ForeignKey(column="reasons.id", ondelete="SET NULL"), nullable=True)
    assigned_admin_id: Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    comment: Mapped[str] = mapped_column(TEXT, nullable=True)
    reason_rejected: Mapped[bool] = mapped_column(TEXT, nullable=True)
    status: Mapped[str] = mapped_column(
        Enum(ReportStatus, values_callable=values_callable, name="report_status_enum"),
        default=ReportStatus.PENDING.value
    )
    reason: Mapped["Report"] = relationship("Reason", back_populates="reports", lazy="joined")
    buller: Mapped["Buller"] = relationship("Buller", back_populates="reports", lazy="joined")
    admin: Mapped["User"] = relationship(
        "User", back_populates="reports_handled", foreign_keys=[assigned_admin_id], lazy="joined")
    reporter: Mapped["User"] = relationship(
        "User", foreign_keys=[reporter_id], back_populates="reports_sent", lazy="joined"
    )

    def __str__(self):
        return f"Report #{self.id} [{self.status}]"


metadata = Base.metadata
