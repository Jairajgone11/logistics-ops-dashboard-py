"""Threshold-based anomaly detection for shipment records."""

from __future__ import annotations

import pandas as pd


def _reason_for_row(row: pd.Series) -> str:
    reasons: list[str] = []
    if row.get("quote_response_hours", 0) > 48:
        reasons.append("quote_response_over_48h")
    if row.get("customs_status") in {"delayed", "rejected"}:
        reasons.append(f"customs_{row.get('customs_status')}")
    if not bool(row.get("supplier_compliance_flag", True)):
        reasons.append("supplier_non_compliant")
    return "; ".join(reasons)


def flag_anomalies(df: pd.DataFrame) -> pd.DataFrame:
    """Return records with operational anomalies and an anomaly_reason column."""
    supplier_non_compliant = ~df["supplier_compliance_flag"].astype(bool)
    mask = (
        (df["quote_response_hours"] > 48)
        | (df["customs_status"].isin({"delayed", "rejected"}))
        | supplier_non_compliant
    )

    flagged = df.loc[mask].copy()
    if flagged.empty:
        flagged["anomaly_reason"] = []
        return flagged

    flagged["anomaly_reason"] = flagged.apply(_reason_for_row, axis=1)
    return flagged
