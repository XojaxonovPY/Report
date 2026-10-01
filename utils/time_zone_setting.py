from datetime import datetime
from zoneinfo import ZoneInfo

UZB_TZ = ZoneInfo("Asia/Tashkent")


def get_current_uzb_time() -> datetime:
    return datetime.now(tz=UZB_TZ)
