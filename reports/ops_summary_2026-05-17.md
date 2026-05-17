# Logistics Operations Summary - 2026-05-17

## Executive Summary

| KPI | Value |
| --- | ---: |
| Total shipments | 5000 |
| Average quote response hours | 19.00 |
| Quotes within 24h | 82.1% |
| Customs clearance rate | 74.9% |
| Supplier compliance rate | 90.4% |
| Fulfilment on-time rate | 78.0% |
| Flagged anomaly records | 1208 |

## Anomaly Alerts

Top 10 flagged records based on threshold checks.

| shipment_id | origin_country | destination_country | transport_mode | quote_response_hours | customs_status | supplier_id | supplier_compliance_flag | anomaly_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SHP-000013 | Centralia | Northland | road | 89.33 | cleared | SUP-0275 | True | quote_response_over_48h |
| SHP-000014 | Highmere | Westhaven | air | 11.00 | cleared | SUP-0135 | False | supplier_non_compliant |
| SHP-000018 | Eastoria | Centralia | rail | 21.07 | delayed | SUP-0103 | True | customs_delayed |
| SHP-000020 | Westhaven | Northland | sea | 17.28 | delayed | SUP-0170 | True | customs_delayed |
| SHP-000025 | Northland | Rivermark | sea | 92.47 | cleared | SUP-0247 | True | quote_response_over_48h |
| SHP-000032 | Eastoria | Westhaven | road | 13.49 | rejected | SUP-0335 | True | customs_rejected |
| SHP-000034 | Westhaven | Lowvale | road | 5.68 | cleared | SUP-0129 | False | supplier_non_compliant |
| SHP-000035 | Southport | Northland | air | 20.08 | pending | SUP-0327 | False | supplier_non_compliant |
| SHP-000036 | Rivermark | Northland | air | 10.84 | delayed | SUP-0077 | True | customs_delayed |
| SHP-000043 | Highmere | Eastoria | air | 26.86 | delayed | SUP-0136 | True | customs_delayed |

## Volume Breakdown

### By Transport Mode

| Category | Shipments |
| --- | ---: |
| air | 890 |
| rail | 702 |
| road | 1831 |
| sea | 1577 |

### By Origin Region

| Category | Shipments |
| --- | ---: |
| Central Region | 1214 |
| Eastern Region | 609 |
| Northern Region | 1270 |
| Southern Region | 1287 |
| Western Region | 620 |

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
