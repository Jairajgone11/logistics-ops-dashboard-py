"""Generate Markdown reports for logistics operations KPIs."""

from __future__ import annotations

import os
from datetime import date
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

try:
    from .anomaly_detector import flag_anomalies
    from .kpi_calculator import (
        avg_quote_response_hours,
        customs_clearance_rate,
        fulfilment_on_time_rate,
        pct_quotes_within_24h,
        supplier_compliance_rate,
        volume_by_transport_mode,
    )
except ImportError:
    from anomaly_detector import flag_anomalies
    from kpi_calculator import (
        avg_quote_response_hours,
        customs_clearance_rate,
        fulfilment_on_time_rate,
        pct_quotes_within_24h,
        supplier_compliance_rate,
        volume_by_transport_mode,
    )


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CLEAN_PATH = PROJECT_ROOT / "data" / "clean_shipments.csv"
DEFAULT_REPORTS_DIR = PROJECT_ROOT / "reports"

REGION_BY_COUNTRY = {
    "Northland": "Northern Region",
    "Southport": "Southern Region",
    "Eastoria": "Eastern Region",
    "Westhaven": "Western Region",
    "Centralia": "Central Region",
    "Highmere": "Northern Region",
    "Lowvale": "Southern Region",
    "Rivermark": "Central Region",
}


def _format_pct(value: float) -> str:
    return f"{value:.1f}%"


def _markdown_table(df: pd.DataFrame) -> str:
    if df.empty:
        return "_No anomaly alerts found._"

    table = df.fillna("").astype(str)
    headers = list(table.columns)
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for _, row in table.iterrows():
        values = [str(row[column]).replace("|", "\\|") for column in headers]
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def _volume_section(title: str, volumes: dict[str, int]) -> str:
    lines = [f"### {title}", "", "| Category | Shipments |", "| --- | ---: |"]
    for category, count in volumes.items():
        lines.append(f"| {category} | {count} |")
    return "\n".join(lines)


def generate_report(
    df: pd.DataFrame,
    output_dir: Path = DEFAULT_REPORTS_DIR,
    report_date: date | None = None,
) -> Path:
    """Generate and save a Markdown operations report."""
    report_date = report_date or date.today()
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"ops_summary_{report_date.isoformat()}.md"

    anomalies = flag_anomalies(df)
    top_anomalies = anomalies.head(10)[
        [
            "shipment_id",
            "origin_country",
            "destination_country",
            "transport_mode",
            "quote_response_hours",
            "customs_status",
            "supplier_id",
            "supplier_compliance_flag",
            "anomaly_reason",
        ]
    ].copy()
    if not top_anomalies.empty:
        top_anomalies["quote_response_hours"] = top_anomalies["quote_response_hours"].map(lambda value: f"{value:.2f}")

    by_mode = volume_by_transport_mode(df)
    by_origin_region = (
        df.assign(origin_region=df["origin_country"].map(REGION_BY_COUNTRY).fillna("Other Region"))
        .groupby("origin_region")
        .size()
        .sort_index()
        .astype(int)
        .to_dict()
    )

    content = f"""# Logistics Operations Summary - {report_date.isoformat()}

## Executive Summary

| KPI | Value |
| --- | ---: |
| Total shipments | {len(df)} |
| Average quote response hours | {avg_quote_response_hours(df):.2f} |
| Quotes within 24h | {_format_pct(pct_quotes_within_24h(df))} |
| Customs clearance rate | {_format_pct(customs_clearance_rate(df))} |
| Supplier compliance rate | {_format_pct(supplier_compliance_rate(df))} |
| Fulfilment on-time rate | {_format_pct(fulfilment_on_time_rate(df))} |
| Flagged anomaly records | {len(anomalies)} |

## Anomaly Alerts

Top 10 flagged records based on threshold checks.

{_markdown_table(top_anomalies)}

## Volume Breakdown

{_volume_section("By Transport Mode", by_mode)}

{_volume_section("By Origin Region", by_origin_region)}

## Recommendations

### Immediate Actions

- Review shipments with quote response times above 48 hours.
- Prioritise customs follow-up for delayed and rejected records.
- Contact suppliers attached to non-compliance alerts.

### Monitoring Focus

- Track quote turnaround against the 24-hour service target.
- Compare fulfilment performance by transport mode each reporting cycle.
- Watch supplier compliance trends for recurring exceptions.

### Next Review

- Re-run this report after the next cleaned data refresh.
"""

    output_path.write_text(content, encoding="utf-8")
    return output_path


def main() -> None:
    load_dotenv(PROJECT_ROOT / ".env")
    clean_path = PROJECT_ROOT / os.getenv("CLEAN_DATA_PATH", "data/clean_shipments.csv")
    reports_dir = PROJECT_ROOT / os.getenv("REPORTS_DIR", "reports")

    df = pd.read_csv(clean_path, parse_dates=["rfq_sent_at", "quote_received_at"])
    report_path = generate_report(df, output_dir=reports_dir)
    print(f"Generated operations report at {report_path}")


if __name__ == "__main__":
    main()
