"""服务器本地时间口径：保存、展示、折叠共用同一套「服务器自然日」。"""

from __future__ import annotations

from datetime import datetime


def to_server_local(dt: datetime) -> datetime:
    """把时刻归一到服务器本地时区。

    aware 时刻换算到服务器本地；naive 时刻按服务器本地解释。
    （``datetime.astimezone()`` 无参调用对两者正是此语义。）
    """
    return dt.astimezone()


def parse_started_at(raw: str) -> datetime:
    """解析表单 datetime-local 墙钟：naive 输入按服务器本地解释，返回 aware 时刻。"""
    return to_server_local(datetime.fromisoformat(raw))
