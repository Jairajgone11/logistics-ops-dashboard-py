import pandas as pd

from src.kpi_calculator import (
    avg_quote_response_hours,
    customs_clearance_rate,
    fulfilment_on_time_rate,
    pct_quotes_within_24h,
    supplier_compliance_rate,
    volume_by_transport_mode,
)


def _sample_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "quote_response_hours": [4.0, 12.0, 30.0, 72.0],
            "customs_status": ["cleared", "pending", "cleared", "delayed"],
            "supplier_compliance_flag": [True, True, False, True],
            "fulfilment_status": ["on_time", "late", "on_time", "failed"],
            "transport_mode": ["air", "sea", "air", "road"],
        }
    )


def test_kpi_functions_return_expected_types_and_ranges() -> None:
    df = _sample_df()

    avg_response = avg_quote_response_hours(df)
    within_24h = pct_quotes_within_24h(df)
    clearance = customs_clearance_rate(df)
    compliance = supplier_compliance_rate(df)
    on_time = fulfilment_on_time_rate(df)
    mode_volume = volume_by_transport_mode(df)

    assert isinstance(avg_response, float)
    assert avg_response >= 0

    for percentage in [within_24h, clearance, compliance, on_time]:
        assert isinstance(percentage, float)
        assert 0 <= percentage <= 100

    assert isinstance(mode_volume, dict)
    assert mode_volume == {"air": 2, "road": 1, "sea": 1}
