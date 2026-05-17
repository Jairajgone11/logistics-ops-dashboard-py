# Logistics Ops Dashboard Py

A small Python analytics project for fictional logistics operations data. It generates synthetic shipment records, cleans and enriches them, calculates operational KPIs, flags anomalies, and writes a Markdown operations report.

All data is fictional. Supplier IDs, shipment IDs, and country names are synthetic and are not intended to represent real companies or real locations.

## Project Structure

```text
logistics-ops-dashboard-py/
  data/                  Raw and processed CSV files
  notebooks/             Plotly visualisation notebook
  reports/               Generated Markdown reports
  src/
    generate_data.py     Synthetic dataset generator
    pipeline.py          Cleaning and transformation pipeline
    kpi_calculator.py    KPI functions
    anomaly_detector.py  Threshold-based anomaly flagging
    reporter.py          Markdown report generator
  tests/                 Pytest unit tests
```

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Optional `.env` values:

```text
SHIPMENT_COUNT=5000
RANDOM_SEED=42
RAW_DATA_PATH=data/raw_shipments.csv
CLEAN_DATA_PATH=data/clean_shipments.csv
REPORTS_DIR=reports
```

## Run The Pipeline

```bash
python src/generate_data.py
python src/pipeline.py
python src/reporter.py
```

The commands create:

- `data/raw_shipments.csv`
- `data/clean_shipments.csv`
- `reports/ops_summary_{date}.md`

## Notebook

Open `notebooks/dashboard.ipynb` after running the generator and pipeline. The notebook uses Plotly to show:

- Quote response time histogram with a 24-hour threshold line
- Customs status pie chart
- Fulfilment rate bar chart by transport mode
- Supplier compliance trend over time

## Tests

```bash
pytest
```

The tests cover KPI return types and ranges, pipeline cleaning behavior, and derived columns.
