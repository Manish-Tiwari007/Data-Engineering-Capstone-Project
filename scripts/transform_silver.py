"""Transform Bronze records into cleaned Silver records."""

from __future__ import annotations

from snowflake_connection import get_connection


def _ensure_silver_table(cursor) -> None:
    """Ensure Silver schema/table/columns exist for rerunnable pipeline."""
    cursor.execute("CREATE SCHEMA IF NOT EXISTS SILVER")
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS SILVER.PATIENT_CLEAN (
            patient_id NUMBER,
            patient_name STRING,
            age NUMBER,
            gender STRING,
            hospital STRING,
            disease STRING,
            admission_date DATE,
            discharge_date DATE,
            stay_days NUMBER,
            treatment_cost NUMBER(18, 2),
            batch_date DATE,
            record_hash STRING
        )
        """
    )
    cursor.execute(
        "ALTER TABLE SILVER.PATIENT_CLEAN ADD COLUMN IF NOT EXISTS batch_date DATE"
    )
    cursor.execute(
        "ALTER TABLE SILVER.PATIENT_CLEAN ADD COLUMN IF NOT EXISTS record_hash STRING"
    )


def transform_to_silver(run_date: str) -> int:
    """Load deduplicated, typed data into `SILVER.PATIENT_CLEAN`.

    Args:
        run_date: Pipeline batch date (`YYYY-MM-DD`).

    Returns:
        Inserted row count.
    """
    conn = get_connection(schema="SILVER")
    cursor = conn.cursor()

    try:
        _ensure_silver_table(cursor)
        cursor.execute(
            "DELETE FROM SILVER.PATIENT_CLEAN WHERE batch_date = %s", (run_date,)
        )

        insert_sql = """
            INSERT INTO SILVER.PATIENT_CLEAN (
                patient_id,
                patient_name,
                age,
                gender,
                hospital,
                disease,
                admission_date,
                discharge_date,
                stay_days,
                treatment_cost,
                batch_date,
                record_hash
            )
            WITH deduped AS (
                SELECT
                    patient_id,
                    TRIM(patient_name) AS patient_name,
                    TRY_TO_NUMBER(age) AS age,
                    UPPER(TRIM(gender)) AS gender,
                    TRIM(hospital) AS hospital,
                    TRIM(disease) AS disease,
                    TRY_TO_DATE(admission_date) AS admission_date,
                    TRY_TO_DATE(discharge_date) AS discharge_date,
                    TRY_TO_DECIMAL(TO_VARCHAR(treatment_cost), 18, 2) AS treatment_cost,
                    batch_date,
                    record_hash,
                    ROW_NUMBER() OVER (
                        PARTITION BY patient_id, batch_date
                        ORDER BY ingested_at DESC
                    ) AS rn
                FROM BRONZE.PATIENT_RAW
                WHERE batch_date = %s::DATE
            )
            SELECT
                patient_id,
                patient_name,
                age,
                CASE WHEN gender IN ('M', 'F') THEN gender ELSE 'U' END AS gender,
                hospital,
                disease,
                admission_date,
                discharge_date,
                DATEDIFF('day', admission_date, discharge_date) AS stay_days,
                treatment_cost,
                batch_date,
                record_hash
            FROM deduped
            WHERE rn = 1
              AND patient_id IS NOT NULL
              AND admission_date IS NOT NULL
              AND discharge_date IS NOT NULL
        """

        cursor.execute(insert_sql, (run_date,))
        inserted = cursor.rowcount if cursor.rowcount and cursor.rowcount > 0 else 0
        conn.commit()
        print(f"Loaded Silver layer for {run_date}. Inserted rows: {inserted}")
        return inserted
    finally:
        cursor.close()
        conn.close()
