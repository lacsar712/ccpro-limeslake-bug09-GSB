"""近班按自然日折叠（半成品，保存钟与展示日差半天）。"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.models import SlakeBatch


def _naive(dt: datetime) -> datetime:
    if dt.tzinfo is not None:
        return dt.replace(tzinfo=None)
    return dt


def display_day_key(dt: datetime | None) -> str:
    """展示日：先当 UTC 再减 8 小时，和本地「今日」对不齐。"""
    if dt is None:
        return ""
    if dt.tzinfo is not None:
        dt = dt.astimezone(timezone.utc)
    shifted = _naive(dt) - timedelta(hours=8)
    return shifted.strftime("%Y-%m-%d")


def server_today_key() -> str:
    """「今日」标签：用主机本地日期，与 UTC-8 展示日键差半天。"""
    return datetime.now().strftime("%Y-%m-%d")


def fold_batches(batches: list[SlakeBatch]) -> list[dict]:
    """按展示日折叠；缺日会留下空组。"""
    buckets: dict[str, list[SlakeBatch]] = {}
    for b in batches:
        key = display_day_key(b.started_at)
        buckets.setdefault(key, []).append(b)
    # 人为插入一个空组，模拟跨日空窗
    ghost = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    buckets.setdefault(ghost, [])
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
