from pathlib import Path

import pandas as pd

from src.pipeline import KEY_COLUMNS, clean_shipments, run_pipeline


def _raw_shipments() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "shipment_id": ["SHP-000001", "SHP-000002", None],
            "origin_country": ["Northland", "Southport", None],
            "destination_country": ["Eastoria", "Westhaven", "Centralia"],
            "transport_mode": ["air", "sea", None],
            "rfq_sent_at": ["2026-01-01 08:00:00", "2026-01-02 09:30:00", "2026-01-03 10:00:00"],
            "quote_received_at": ["2026-01-01 20:00:00", "2026-01-04 09:30:00", "2026-01-03 14:30:00"],
            "customs_status": ["cleared", "delayed", None],
            "supplier_id": ["SUP-0001", None, "SUP-0003"],
            "supplier_compliance_flag": [True, False, None],
            "fulfilment_status": ["on_time", "late", None],
        }
    )


def test_clean_shipments_fills_key_nulls_and_adds_derived_columns() -> None:
    cleaned = clean_shipments(_raw_shipments())

    assert "quote_response_hours" in cleaned.columns
    assert cleaned[KEY_COLUMNS].isna().sum().sum() == 0
    assert cleaned["quote_response_hours"].tolist() == [12.0, 48.0, 4.5]


def test_run_pipeline_saves_clean_csv(tmp_path: Path) -> None:
    raw_path = tmp_path / "raw_shipments.csv"
    clean_path = tmp_path / "clean_shipments.csv"
    _raw_shipments().to_csv(raw_path, index=False)

    cleaned = run_pipeline(input_path=raw_path, output_path=clean_path)

    assert clean_path.exists()
    assert "quote_response_hours" in pd.read_csv(clean_path).columns
    assert len(cleaned) == 3
