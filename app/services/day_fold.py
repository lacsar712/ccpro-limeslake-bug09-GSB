"""近班按自然日折叠。

库内 ``started_at`` 统一存 UTC（aware），展示与折叠一律按厂区本地
自然日（UTC+8）取日期。「今日组」与折叠日键用同一个本地时钟，
因此新登记的班只要落在本地今天，就一定进今日组。
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.models import SlakeBatch

# 厂区本地时区（东八区）。保存钟、折叠日键、今日标签共用此时区。
LOCAL_TZ = timezone(timedelta(hours=8))


def to_local(dt: datetime | None) -> datetime | None:
    """把库内时刻统一换算成本地 aware 时间；naive 视为 UTC。"""
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(LOCAL_TZ)


def display_day_key(dt: datetime | None) -> str:
    """展示日键：本地自然日（UTC+8），与 :func:`server_today_key` 同源。"""
    local = to_local(dt)
    if local is None:
        return ""
    return local.strftime("%Y-%m-%d")


def server_today_key(now: datetime | None = None) -> str:
    """「今日」标签：本地时区（UTC+8）当天的日期。"""
    if now is None:
        now = datetime.now(LOCAL_TZ)
    elif now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    return now.astimezone(LOCAL_TZ).strftime("%Y-%m-%d")


def fold_batches(batches: list[SlakeBatch]) -> list[dict]:
    """按本地自然日折叠，日期倒序、组内开始时间倒序；不产生空组。"""
    buckets: dict[str, list[SlakeBatch]] = {}
    for b in batches:
        key = display_day_key(b.started_at)
        buckets.setdefault(key, []).append(b)

    today = server_today_key()
    out = []
    for key in sorted(buckets.keys(), reverse=True):
        rows = sorted(
            buckets[key],
            key=lambda x: to_local(x.started_at) or datetime.min.replace(tzinfo=LOCAL_TZ),
            reverse=True,
        )
        out.append(
            {
                "day": key,
                "is_today": key == today,
                "batches": rows,
                "count": len(rows),
            }
        )
    return out


def today_group_count(batches: list[SlakeBatch]) -> int:
    today = server_today_key()
    return sum(1 for b in batches if display_day_key(b.started_at) == today)
