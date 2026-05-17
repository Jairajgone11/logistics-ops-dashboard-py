"""Build a static Vercel dashboard from the cleaned shipment CSV."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CLEAN_DATA_PATH = PROJECT_ROOT / "data" / "clean_shipments.csv"
PUBLIC_DIR = PROJECT_ROOT / "public"


def _parse_bool(value: str) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


def _read_records() -> list[dict[str, object]]:
    with CLEAN_DATA_PATH.open(newline="", encoding="utf-8") as csv_file:
        records = list(csv.DictReader(csv_file))

    for record in records:
        record["quote_response_hours"] = float(record["quote_response_hours"])
        record["supplier_compliance_flag"] = _parse_bool(str(record["supplier_compliance_flag"]))
    return records


def _percentage(part: int, total: int) -> float:
    if total == 0:
        return 0.0
    return round((part / total) * 100, 1)


def _anomaly_reasons(record: dict[str, object]) -> list[str]:
    reasons: list[str] = []
    if float(record["quote_response_hours"]) > 48:
        reasons.append("Quote response over 48h")
    if record["customs_status"] in {"delayed", "rejected"}:
        reasons.append(f"Customs {record['customs_status']}")
    if not bool(record["supplier_compliance_flag"]):
        reasons.append("Supplier non-compliant")
    return reasons


def _week_start(value: str) -> str:
    dt = datetime.fromisoformat(value)
    start = dt.date().toordinal() - dt.weekday()
    return datetime.fromordinal(start).date().isoformat()


def build_dashboard_data(records: list[dict[str, object]]) -> dict[str, object]:
    total = len(records)
    quote_hours = [float(record["quote_response_hours"]) for record in records]
    customs_counts = Counter(str(record["customs_status"]) for record in records)
    mode_counts = Counter(str(record["transport_mode"]) for record in records)

    fulfilment_by_mode: dict[str, dict[str, int]] = defaultdict(lambda: {"total": 0, "on_time": 0})
    compliance_by_week: dict[str, dict[str, int]] = defaultdict(lambda: {"total": 0, "compliant": 0})
    anomalies: list[dict[str, object]] = []

    for record in records:
        mode = str(record["transport_mode"])
        fulfilment_by_mode[mode]["total"] += 1
        if record["fulfilment_status"] == "on_time":
            fulfilment_by_mode[mode]["on_time"] += 1

        week = _week_start(str(record["rfq_sent_at"]))
        compliance_by_week[week]["total"] += 1
        if bool(record["supplier_compliance_flag"]):
            compliance_by_week[week]["compliant"] += 1

        reasons = _anomaly_reasons(record)
        if reasons and len(anomalies) < 10:
            anomalies.append(
                {
                    "shipment_id": record["shipment_id"],
                    "origin_country": record["origin_country"],
                    "destination_country": record["destination_country"],
                    "transport_mode": record["transport_mode"],
                    "quote_response_hours": round(float(record["quote_response_hours"]), 2),
                    "customs_status": record["customs_status"],
                    "supplier_id": record["supplier_id"],
                    "reason": "; ".join(reasons),
                }
            )

    fulfilment_rates = {
        mode: _percentage(values["on_time"], values["total"])
        for mode, values in sorted(fulfilment_by_mode.items())
    }
    compliance_trend = [
        {
            "week": week,
            "rate": _percentage(values["compliant"], values["total"]),
        }
        for week, values in sorted(compliance_by_week.items())
    ]

    return {
        "kpis": {
            "total_shipments": total,
            "avg_quote_response_hours": round(sum(quote_hours) / total, 2) if total else 0,
            "pct_quotes_within_24h": _percentage(sum(value <= 24 for value in quote_hours), total),
            "customs_clearance_rate": _percentage(customs_counts["cleared"], total),
            "supplier_compliance_rate": _percentage(
                sum(bool(record["supplier_compliance_flag"]) for record in records), total
            ),
            "fulfilment_on_time_rate": _percentage(
                sum(record["fulfilment_status"] == "on_time" for record in records), total
            ),
        },
        "quote_response_hours": quote_hours,
        "customs_counts": dict(sorted(customs_counts.items())),
        "mode_counts": dict(sorted(mode_counts.items())),
        "fulfilment_rates_by_mode": fulfilment_rates,
        "compliance_trend": compliance_trend,
        "anomalies": anomalies,
    }


def build_index_html() -> str:
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Logistics Ops Dashboard</title>
  <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
  <style>
    :root { color-scheme: light dark; font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
    body { margin: 0; background: #0f172a; color: #e2e8f0; }
    main { max-width: 1180px; margin: 0 auto; padding: 32px 20px 56px; }
    h1 { margin: 0 0 8px; font-size: clamp(2rem, 4vw, 3.5rem); }
    h2 { margin: 32px 0 16px; }
    .muted { color: #94a3b8; }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 16px; }
    .card, .chart, table { background: #111c33; border: 1px solid #24324d; border-radius: 16px; }
    .card { padding: 18px; }
    .label { color: #94a3b8; font-size: 0.88rem; }
    .value { font-size: 1.8rem; font-weight: 700; margin-top: 8px; }
    .chart { min-height: 380px; padding: 10px; }
    .charts { display: grid; grid-template-columns: repeat(auto-fit, minmax(360px, 1fr)); gap: 18px; }
    table { width: 100%; border-collapse: collapse; overflow: hidden; }
    th, td { border-bottom: 1px solid #24324d; padding: 12px; text-align: left; font-size: 0.92rem; }
    th { color: #cbd5e1; background: #17233b; }
    tr:last-child td { border-bottom: 0; }
    a { color: #93c5fd; }
  </style>
</head>
<body>
  <main>
    <p class="muted">Fictional logistics operations data</p>
    <h1>Logistics Ops Dashboard</h1>
    <p class="muted">Static Vercel dashboard generated from <code>data/clean_shipments.csv</code>.</p>

    <section class="grid" id="kpiCards"></section>

    <h2>Operations Charts</h2>
    <section class="charts">
      <div class="chart" id="quoteHistogram"></div>
      <div class="chart" id="customsPie"></div>
      <div class="chart" id="fulfilmentBar"></div>
      <div class="chart" id="complianceTrend"></div>
    </section>

    <h2>Anomaly Alerts</h2>
    <p class="muted">Top 10 records flagged for slow quote response, customs issues, or supplier non-compliance.</p>
    <div id="anomalyTable"></div>
  </main>

  <script>
    const plotLayout = {
      paper_bgcolor: "#111c33",
      plot_bgcolor: "#111c33",
      font: { color: "#e2e8f0" },
      margin: { t: 54, r: 24, b: 52, l: 56 }
    };

    const pct = (value) => `${value.toFixed(1)}%`;

    fetch("./dashboard-data.json")
      .then((response) => response.json())
      .then((data) => {
        const cards = [
          ["Total Shipments", data.kpis.total_shipments.toLocaleString()],
          ["Avg Quote Response", `${data.kpis.avg_quote_response_hours.toFixed(2)}h`],
          ["Quotes Within 24h", pct(data.kpis.pct_quotes_within_24h)],
          ["Customs Clearance", pct(data.kpis.customs_clearance_rate)],
          ["Supplier Compliance", pct(data.kpis.supplier_compliance_rate)],
          ["On-Time Fulfilment", pct(data.kpis.fulfilment_on_time_rate)]
        ];

        document.getElementById("kpiCards").innerHTML = cards.map(([label, value]) => `
          <article class="card"><div class="label">${label}</div><div class="value">${value}</div></article>
        `).join("");

        Plotly.newPlot("quoteHistogram", [
          { x: data.quote_response_hours, type: "histogram", marker: { color: "#38bdf8" }, name: "Response hours" }
        ], {
          ...plotLayout,
          title: "Quote Response Time Histogram",
          xaxis: { title: "Hours" },
          yaxis: { title: "Shipments" },
          shapes: [{ type: "line", x0: 24, x1: 24, y0: 0, y1: 1, yref: "paper", line: { color: "#f97316", dash: "dash" } }],
          annotations: [{ x: 24, y: 1, yref: "paper", text: "24h target", showarrow: false, xanchor: "left", yanchor: "bottom" }]
        }, { responsive: true });

        Plotly.newPlot("customsPie", [
          { labels: Object.keys(data.customs_counts), values: Object.values(data.customs_counts), type: "pie", hole: 0.35 }
        ], { ...plotLayout, title: "Customs Status Breakdown" }, { responsive: true });

        Plotly.newPlot("fulfilmentBar", [
          { x: Object.keys(data.fulfilment_rates_by_mode), y: Object.values(data.fulfilment_rates_by_mode), type: "bar", marker: { color: "#22c55e" } }
        ], {
          ...plotLayout,
          title: "Fulfilment On-Time Rate By Mode",
          yaxis: { title: "On-time rate (%)", range: [0, 100] },
          xaxis: { title: "Transport mode" }
        }, { responsive: true });

        Plotly.newPlot("complianceTrend", [
          { x: data.compliance_trend.map((row) => row.week), y: data.compliance_trend.map((row) => row.rate), type: "scatter", mode: "lines+markers", line: { color: "#a78bfa" } }
        ], {
          ...plotLayout,
          title: "Supplier Compliance Trend",
          yaxis: { title: "Compliance rate (%)", range: [0, 100] },
          xaxis: { title: "RFQ week" }
        }, { responsive: true });

        const rows = data.anomalies.map((row) => `
          <tr>
            <td>${row.shipment_id}</td><td>${row.origin_country}</td><td>${row.destination_country}</td>
            <td>${row.transport_mode}</td><td>${row.quote_response_hours}</td><td>${row.customs_status}</td>
            <td>${row.supplier_id}</td><td>${row.reason}</td>
          </tr>
        `).join("");
        document.getElementById("anomalyTable").innerHTML = `
          <table>
            <thead><tr><th>Shipment</th><th>Origin</th><th>Destination</th><th>Mode</th><th>Quote Hours</th><th>Customs</th><th>Supplier</th><th>Reason</th></tr></thead>
            <tbody>${rows}</tbody>
          </table>
        `;
      });
  </script>
</body>
</html>
"""


def main() -> None:
    if not CLEAN_DATA_PATH.exists():
        raise FileNotFoundError(
            f"Missing {CLEAN_DATA_PATH}. Run `python src/generate_data.py` and `python src/pipeline.py` first."
        )

    PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
    dashboard_data = build_dashboard_data(_read_records())
    (PUBLIC_DIR / "dashboard-data.json").write_text(json.dumps(dashboard_data, indent=2), encoding="utf-8")
    (PUBLIC_DIR / "index.html").write_text(build_index_html(), encoding="utf-8")
    print(f"Built Vercel static site in {PUBLIC_DIR}")


if __name__ == "__main__":
    main()
