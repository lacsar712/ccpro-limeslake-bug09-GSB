"""近班按自然日折叠：展示日与「今日」都跟服务器自然日走。"""

from __future__ import annotations

from datetime import datetime, timezone

from app.models import SlakeBatch
from app.services.timekit import to_server_local


def display_day_key(dt: datetime | None) -> str:
    """展示日键：时刻换算到服务器本地后取自然日。"""
    if dt is None:
        return ""
    return to_server_local(dt).strftime("%Y-%m-%d")


def server_today_key() -> str:
    """「今日」标签：服务器本地日期，与展示日键同口径。"""
    return datetime.now().astimezone().strftime("%Y-%m-%d")


def fold_batches(batches: list[SlakeBatch]) -> list[dict]:
    """按服务器自然日折叠；只折叠库内真实批次，不留空组。"""
    buckets: dict[str, list[SlakeBatch]] = {}
    for b in batches:
        key = display_day_key(b.started_at)
        buckets.setdefault(key, []).append(b)
    today = server_today_key()
    ordered_keys = sorted(buckets.keys(), reverse=True)
    out = []
    for key in ordered_keys:
        rows = sorted(
            buckets[key],
            key=lambda x: x.started_at or datetime.min.replace(tzinfo=timezone.utc),
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
