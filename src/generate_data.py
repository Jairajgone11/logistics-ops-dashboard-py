"""Generate fictional logistics shipment data."""

from __future__ import annotations

import os
import random
from datetime import timedelta
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from faker import Faker


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RAW_PATH = PROJECT_ROOT / "data" / "raw_shipments.csv"

TRANSPORT_MODES = ("air", "sea", "road", "rail")
CUSTOMS_STATUSES = ("cleared", "pending", "delayed", "rejected")
FULFILMENT_STATUSES = ("on_time", "late", "failed")
FICTIONAL_COUNTRIES = (
    "Northland",
    "Southport",
    "Eastoria",
    "Westhaven",
    "Centralia",
    "Highmere",
    "Lowvale",
    "Rivermark",
)


def _weighted_choice(options: tuple[str, ...], weights: tuple[float, ...]) -> str:
    return random.choices(options, weights=weights, k=1)[0]


def _quote_delay_hours() -> float:
    delay_bucket = random.random()
    if delay_bucket < 0.82:
        return round(random.uniform(1, 24), 2)
    if delay_bucket < 0.94:
        return round(random.uniform(24.1, 48), 2)
    return round(random.uniform(48.1, 96), 2)


def generate_shipments(record_count: int = 5000, seed: int = 42) -> pd.DataFrame:
    """Return a synthetic shipment dataset with fictional logistics records."""
    fake = Faker()
    Faker.seed(seed)
    random.seed(seed)

    records: list[dict[str, object]] = []
    for index in range(1, record_count + 1):
        origin = random.choice(FICTIONAL_COUNTRIES)
        destination_choices = [country for country in FICTIONAL_COUNTRIES if country != origin]
        rfq_sent_at = fake.date_time_between(start_date="-180d", end_date="now")
        delay_hours = _quote_delay_hours()

        records.append(
            {
                "shipment_id": f"SHP-{index:06d}",
                "origin_country": origin,
                "destination_country": random.choice(destination_choices),
                "transport_mode": _weighted_choice(TRANSPORT_MODES, (0.18, 0.32, 0.36, 0.14)),
                "rfq_sent_at": rfq_sent_at.isoformat(sep=" "),
                "quote_received_at": (rfq_sent_at + timedelta(hours=delay_hours)).isoformat(sep=" "),
                "customs_status": _weighted_choice(CUSTOMS_STATUSES, (0.76, 0.13, 0.08, 0.03)),
                "supplier_id": f"SUP-{random.randint(1, 350):04d}",
                "supplier_compliance_flag": random.random() < 0.90,
                "fulfilment_status": _weighted_choice(FULFILMENT_STATUSES, (0.78, 0.17, 0.05)),
            }
        )

    return pd.DataFrame.from_records(records)


def save_shipments(df: pd.DataFrame, output_path: Path = DEFAULT_RAW_PATH) -> Path:
    """Save shipments to CSV and return the output path."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    return output_path


def main() -> None:
    load_dotenv(PROJECT_ROOT / ".env")
    record_count = int(os.getenv("SHIPMENT_COUNT", "5000"))
    seed = int(os.getenv("RANDOM_SEED", "42"))
    output_path = PROJECT_ROOT / os.getenv("RAW_DATA_PATH", "data/raw_shipments.csv")

    saved_path = save_shipments(generate_shipments(record_count=record_count, seed=seed), output_path)
    print(f"Generated {record_count} fictional shipment records at {saved_path}")


if __name__ == "__main__":
    main()
