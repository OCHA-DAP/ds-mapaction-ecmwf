from typing import Any, Dict, List

from src.data_retrieval.cds.ecmwf import get_ecmwf_cds_metadata


def test_get_ecmwf_cds_metadata_returns_correct_value():
    years: List[int] = [2021, 2021]
    months: List[int] = [1, 2, 3]
    leadtime_months: List[int] = [1, 2, 3]
    expected: Dict[str, Any] = {
        "product_type": "monthly_mean",
        "format": "grib",
        "originating_centre": "ecmwf",
        "system": "51",
        "variable": ["total_precipitation"],
        "year": ["2021", "2021"],
        "month": ["01", "02", "03"],
        "leadtime_month": ["1", "2", "3"],
    }

    returned: Dict[str, Any] = get_ecmwf_cds_metadata(
        years, months, leadtime_months
    )

    assert expected == returned
