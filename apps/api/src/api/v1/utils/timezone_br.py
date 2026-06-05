"""Fuso operacional Brasil (America/Sao_Paulo) com fallback para UTC-3."""

from datetime import timedelta, timezone

try:
    from zoneinfo import ZoneInfo

    BRAZIL_TZ = ZoneInfo("America/Sao_Paulo")
except Exception:
    BRAZIL_TZ = timezone(timedelta(hours=-3))
