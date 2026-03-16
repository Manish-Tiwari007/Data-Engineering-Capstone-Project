"""Extract raw healthcare records from CSV."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, List

import pandas as pd


def _resolve_data_path() -> str:
    """Resolve CSV path for both local and Docker/Airflow execution."""
    env_path = os.getenv("DATA_FILE_PATH")
    if env_path:
        return env_path

    airflow_default = "/opt/airflow/data/patient_data.csv"
    if Path(airflow_default).exists():
        return airflow_default

    project_path = Path(__file__).resolve().parents[1] / "data" / "patient_data.csv"
    return str(project_path)


def extract_data(run_date: str) -> List[Dict[str, object]]:
    """Extract records and enrich with pipeline batch metadata.

    Args:
        run_date: Airflow logical date in YYYY-MM-DD format.

    Returns:
        List of JSON-serializable dictionaries for XCom transfer.
    """
    file_path = _resolve_data_path()
    df = pd.read_csv(file_path)

    df["admission_date"] = pd.to_datetime(df["admission_date"], errors="coerce").dt.date
    df["discharge_date"] = pd.to_datetime(df["discharge_date"], errors="coerce").dt.date
    df["batch_date"] = run_date

    records = df.to_dict(orient="records")
    print(
        f"Extracted {len(records)} records from {file_path} for batch_date={run_date}"
    )
    return records
