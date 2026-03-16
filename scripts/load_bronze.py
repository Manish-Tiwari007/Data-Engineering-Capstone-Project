"""Load extracted records into Bronze layer."""

from __future__ import annotations

import hashlib
from typing import Dict, List

from snowflake_connection import get_connection


def _ensure_bronze_table(cursor) -> None:
    """Ensure Bronze schema/table/columns exist for backward compatibility."""
    cursor.execute("CREATE SCHEMA IF NOT EXISTS BRONZE")
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS BRONZE.PATIENT_RAW (
            patient_id NUMBER,
            patient_name STRING,
            age NUMBER,
            gender STRING,
            hospital STRING,
            disease STRING,
            admission_date DATE,
            discharge_date DATE,
            treatment_cost NUMBER(18, 2),
            ingested_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
            batch_date DATE,
            record_hash STRING
        )
        """
    )
    cursor.execute(
        (
            "ALTER TABLE BRONZE.PATIENT_RAW "
            "ADD COLUMN IF NOT EXISTS ingested_at TIMESTAMP_NTZ"
        )
    )
    cursor.execute(
        "ALTER TABLE BRONZE.PATIENT_RAW ADD COLUMN IF NOT EXISTS batch_date DATE"
    )
    cursor.execute(
        "ALTER TABLE BRONZE.PATIENT_RAW ADD COLUMN IF NOT EXISTS record_hash STRING"
    )


def load_to_bronze(records: List[Dict[str, object]], run_date: str) -> int:
    """Load data into `BRONZE.PATIENT_RAW` in an idempotent way.

    Args:
        records: Extracted records from CSV.
        run_date: Pipeline batch date (`YYYY-MM-DD`).

    Returns:
        Inserted row count.
    """
    if not records:
        return 0

    conn = get_connection(schema="BRONZE")
    cursor = conn.cursor()

    try:
        _ensure_bronze_table(cursor)
        # Idempotency: rerun for same date will replace that date's raw snapshot.
        cursor.execute(
            "DELETE FROM BRONZE.PATIENT_RAW WHERE batch_date = %s", (run_date,)
        )

        insert_sql = """
            INSERT INTO BRONZE.PATIENT_RAW (
                patient_id,
                patient_name,
                age,
                gender,
                hospital,
                disease,
                admission_date,
                discharge_date,
                treatment_cost,
                ingested_at,
                batch_date,
                record_hash
            )
            VALUES (
                %s, %s, %s, %s, %s, %s,
                %s::DATE, %s::DATE, %s,
                CURRENT_TIMESTAMP(),
                %s::DATE,
                %s
            )
        """

        payload = []
        for row in records:
            hash_input = "|".join(
                [
                    str(row.get("patient_id", "")),
                    str(row.get("patient_name", "")),
                    str(row.get("age", "")),
                    str(row.get("gender", "")),
                    str(row.get("hospital", "")),
                    str(row.get("disease", "")),
                    str(row.get("admission_date", "")),
                    str(row.get("discharge_date", "")),
                    str(row.get("treatment_cost", "")),
                    str(run_date),
                ]
            )
            record_hash = hashlib.sha256(hash_input.encode("utf-8")).hexdigest()

            payload.append(
                (
                    row.get("patient_id"),
                    row.get("patient_name"),
                    row.get("age"),
                    row.get("gender"),
                    row.get("hospital"),
                    row.get("disease"),
                    row.get("admission_date"),
                    row.get("discharge_date"),
                    row.get("treatment_cost"),
                    run_date,
                    record_hash,
                )
            )

        cursor.executemany(insert_sql, payload)
        conn.commit()
        print(f"Loaded {len(payload)} rows into BRONZE.PATIENT_RAW for {run_date}")
        return len(payload)
    finally:
        cursor.close()
        conn.close()
