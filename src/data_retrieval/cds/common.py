from typing import Any, Dict

import cdsapi


def download_cds(name: str, metadata: Dict[str, Any], file_path: str):
    client = cdsapi.Client()

    client.retrieve(
        name,
        metadata,
        file_path,
    )

    print(f"Downloaded: {file_path}")
