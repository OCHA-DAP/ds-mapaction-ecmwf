from typing import Any, Dict, List

from src.data_retrieval.cds.era5 import get_era5_cds_metadata


def test_get_era5_cds_metadata_returns_correct_value():
    years: List[int] = [2021, 2021]
    months: List[int] = [1, 2, 3]
    file_type: str = "crib"
    expected: Dict[str, Any] = {
        "product_type": "monthly_averaged_reanalysis",
        "variable": "total_precipitation",
        "year": ["2021", "2021"],
        "month": ["01", "02", "03"],
        "time": "00:00",
        "format": "crib",
    }

    returned: Dict[str, Any] = get_era5_cds_metadata(years, months, file_type)

    assert expected == returned
