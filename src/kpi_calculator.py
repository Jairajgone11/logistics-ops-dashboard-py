"""Operational KPI calculations for logistics shipment data."""

from __future__ import annotations

import pandas as pd


def avg_quote_response_hours(df: pd.DataFrame) -> float:
    """Return the average quote response time in hours."""
    return float(df["quote_response_hours"].mean())


def pct_quotes_within_24h(df: pd.DataFrame) -> float:
    """Return the percentage of quotes received within 24 hours."""
    if len(df) == 0:
        return 0.0
    return float((df["quote_response_hours"] <= 24).mean() * 100)


def customs_clearance_rate(df: pd.DataFrame) -> float:
    """Return the percentage of shipments with cleared customs."""
    if len(df) == 0:
        return 0.0
    return float((df["customs_status"] == "cleared").mean() * 100)


def supplier_compliance_rate(df: pd.DataFrame) -> float:
    """Return the percentage of shipments from compliant suppliers."""
    if len(df) == 0:
        return 0.0
    compliance = df["supplier_compliance_flag"].astype(bool)
    return float(compliance.mean() * 100)


def fulfilment_on_time_rate(df: pd.DataFrame) -> float:
    """Return the percentage of shipments fulfilled on time."""
    if len(df) == 0:
        return 0.0
    return float((df["fulfilment_status"] == "on_time").mean() * 100)


def volume_by_transport_mode(df: pd.DataFrame) -> dict[str, int]:
    """Return shipment counts by transport mode."""
    return {str(mode): int(count) for mode, count in df["transport_mode"].value_counts().sort_index().items()}
