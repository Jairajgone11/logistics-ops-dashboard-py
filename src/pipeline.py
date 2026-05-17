"""Clean and transform fictional logistics shipment data."""

from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RAW_PATH = PROJECT_ROOT / "data" / "raw_shipments.csv"
DEFAULT_CLEAN_PATH = PROJECT_ROOT / "data" / "clean_shipments.csv"

TRANSPORT_MODES = {"air", "sea", "road", "rail"}
CUSTOMS_STATUSES = {"cleared", "pending", "delayed", "rejected"}
FULFILMENT_STATUSES = {"on_time", "late", "failed"}
KEY_COLUMNS = [
    "shipment_id",
    "origin_country",
    "destination_country",
    "transport_mode",
    "rfq_sent_at",
    "quote_received_at",
    "customs_status",
    "supplier_id",
    "supplier_compliance_flag",
    "fulfilment_status",
]


def load_raw_data(input_path: Path = DEFAULT_RAW_PATH) -> pd.DataFrame:
    """Load raw shipment CSV data."""
    return pd.read_csv(input_path)


def _normalise_text_column(series: pd.Series, default: str) -> pd.Series:
    return series.fillna(default).astype(str).str.strip().str.lower()


def _parse_bool(value: object) -> bool:
    if isinstance(value, bool):
        return value
    if pd.isna(value):
        return False
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


def _validate_allowed_values(df: pd.DataFrame, column: str, allowed_values: set[str]) -> None:
    invalid_values = set(df[column].dropna().unique()) - allowed_values
    if invalid_values:
        raise ValueError(f"Invalid values for {column}: {sorted(invalid_values)}")


def clean_shipments(df: pd.DataFrame) -> pd.DataFrame:
    """Clean, validate, and enrich raw shipment data."""
    missing_columns = set(KEY_COLUMNS) - set(df.columns)
    if missing_columns:
        raise ValueError(f"Missing required columns: {sorted(missing_columns)}")

    cleaned = df.copy()
    cleaned["shipment_id"] = cleaned["shipment_id"].fillna("UNKNOWN-SHIPMENT").astype(str).str.strip()
    cleaned["origin_country"] = cleaned["origin_country"].fillna("Unknown Region").astype(str).str.strip()
    cleaned["destination_country"] = cleaned["destination_country"].fillna("Unknown Region").astype(str).str.strip()
    cleaned["supplier_id"] = cleaned["supplier_id"].fillna("SUP-UNKNOWN").astype(str).str.strip()

    cleaned["transport_mode"] = _normalise_text_column(cleaned["transport_mode"], "road")
    cleaned["customs_status"] = _normalise_text_column(cleaned["customs_status"], "pending")
    cleaned["fulfilment_status"] = _normalise_text_column(cleaned["fulfilment_status"], "late")
    cleaned["supplier_compliance_flag"] = cleaned["supplier_compliance_flag"].map(_parse_bool)

    _validate_allowed_values(cleaned, "transport_mode", TRANSPORT_MODES)
    _validate_allowed_values(cleaned, "customs_status", CUSTOMS_STATUSES)
    _validate_allowed_values(cleaned, "fulfilment_status", FULFILMENT_STATUSES)

    cleaned["rfq_sent_at"] = pd.to_datetime(cleaned["rfq_sent_at"], errors="coerce")
    cleaned["quote_received_at"] = pd.to_datetime(cleaned["quote_received_at"], errors="coerce")
    cleaned = cleaned.dropna(subset=["rfq_sent_at", "quote_received_at"]).reset_index(drop=True)

    cleaned["quote_response_hours"] = (
        cleaned["quote_received_at"] - cleaned["rfq_sent_at"]
    ).dt.total_seconds() / 3600

    return cleaned


def save_clean_data(df: pd.DataFrame, output_path: Path = DEFAULT_CLEAN_PATH) -> Path:
    """Save cleaned shipment data to CSV and return the output path."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    return output_path


def run_pipeline(
    input_path: Path = DEFAULT_RAW_PATH,
    output_path: Path = DEFAULT_CLEAN_PATH,
) -> pd.DataFrame:
    """Run the cleaning pipeline and persist the cleaned dataset."""
    cleaned = clean_shipments(load_raw_data(input_path))
    save_clean_data(cleaned, output_path)
    return cleaned


def main() -> None:
    load_dotenv(PROJECT_ROOT / ".env")
    input_path = PROJECT_ROOT / os.getenv("RAW_DATA_PATH", "data/raw_shipments.csv")
    output_path = PROJECT_ROOT / os.getenv("CLEAN_DATA_PATH", "data/clean_shipments.csv")

    cleaned = run_pipeline(input_path=input_path, output_path=output_path)
    print(f"Saved {len(cleaned)} cleaned shipment records at {output_path}")


if __name__ == "__main__":
    main()
