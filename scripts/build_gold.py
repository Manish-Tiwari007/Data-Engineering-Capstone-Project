"""Build Gold layer star schema and summary metrics."""

from __future__ import annotations

from snowflake_connection import get_connection


def _ensure_gold_tables(cursor) -> None:
    """Ensure minimum Gold objects exist before merges/upserts run."""
    cursor.execute("CREATE SCHEMA IF NOT EXISTS GOLD")
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS GOLD.DIM_HOSPITAL (
            hospital_sk NUMBER AUTOINCREMENT,
            hospital_name STRING,
            CONSTRAINT PK_DIM_HOSPITAL PRIMARY KEY (hospital_sk)
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS GOLD.DIM_DISEASE (
            disease_sk NUMBER AUTOINCREMENT,
            disease_name STRING,
            CONSTRAINT PK_DIM_DISEASE PRIMARY KEY (disease_sk)
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS GOLD.DIM_DATE (
            date_sk NUMBER AUTOINCREMENT,
            date_value DATE,
            day_of_week NUMBER,
            month_num NUMBER,
            quarter_num NUMBER,
            year_num NUMBER,
            CONSTRAINT PK_DIM_DATE PRIMARY KEY (date_sk)
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS GOLD.DIM_PATIENT (
            patient_sk NUMBER AUTOINCREMENT,
            patient_id NUMBER,
            patient_name STRING,
            age NUMBER,
            gender STRING,
            valid_from DATE,
            valid_to DATE,
            is_current BOOLEAN,
            CONSTRAINT PK_DIM_PATIENT PRIMARY KEY (patient_sk)
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS GOLD.FACT_TREATMENT (
            treatment_fact_id NUMBER AUTOINCREMENT,
            patient_sk NUMBER,
            hospital_sk NUMBER,
            disease_sk NUMBER,
            admission_date_sk NUMBER,
            discharge_date_sk NUMBER,
            patient_id NUMBER,
            treatment_cost NUMBER(18, 2),
            stay_days NUMBER,
            batch_date DATE,
            inserted_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
            CONSTRAINT PK_FACT_TREATMENT PRIMARY KEY (treatment_fact_id)
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS GOLD.DAILY_SUMMARY_REPORT (
            report_date DATE,
            total_rows_processed NUMBER,
            total_treatment_cost NUMBER(18, 2),
            avg_stay_days NUMBER(18, 2),
            unique_patients NUMBER,
            updated_at TIMESTAMP_NTZ,
            CONSTRAINT PK_DAILY_SUMMARY PRIMARY KEY (report_date)
        )
        """
    )

    # Backward compatibility: repair columns on previously created tables.
    cursor.execute(
        "ALTER TABLE GOLD.DIM_HOSPITAL ADD COLUMN IF NOT EXISTS hospital_sk NUMBER"
    )
    cursor.execute(
        "ALTER TABLE GOLD.DIM_HOSPITAL ADD COLUMN IF NOT EXISTS hospital_name STRING"
    )
    cursor.execute(
        "ALTER TABLE GOLD.DIM_DISEASE ADD COLUMN IF NOT EXISTS disease_sk NUMBER"
    )
    cursor.execute(
        "ALTER TABLE GOLD.DIM_DISEASE ADD COLUMN IF NOT EXISTS disease_name STRING"
    )

    cursor.execute("ALTER TABLE GOLD.DIM_DATE ADD COLUMN IF NOT EXISTS date_sk NUMBER")
    cursor.execute("ALTER TABLE GOLD.DIM_DATE ADD COLUMN IF NOT EXISTS date_value DATE")
    cursor.execute(
        "ALTER TABLE GOLD.DIM_DATE ADD COLUMN IF NOT EXISTS day_of_week NUMBER"
    )
    cursor.execute(
        "ALTER TABLE GOLD.DIM_DATE ADD COLUMN IF NOT EXISTS month_num NUMBER"
    )
    cursor.execute(
        "ALTER TABLE GOLD.DIM_DATE ADD COLUMN IF NOT EXISTS quarter_num NUMBER"
    )
    cursor.execute("ALTER TABLE GOLD.DIM_DATE ADD COLUMN IF NOT EXISTS year_num NUMBER")

    cursor.execute(
        "ALTER TABLE GOLD.DIM_PATIENT ADD COLUMN IF NOT EXISTS patient_sk NUMBER"
    )
    cursor.execute(
        "ALTER TABLE GOLD.DIM_PATIENT ADD COLUMN IF NOT EXISTS patient_id NUMBER"
    )
    cursor.execute(
        "ALTER TABLE GOLD.DIM_PATIENT ADD COLUMN IF NOT EXISTS patient_name STRING"
    )
    cursor.execute("ALTER TABLE GOLD.DIM_PATIENT ADD COLUMN IF NOT EXISTS age NUMBER")
    cursor.execute(
        "ALTER TABLE GOLD.DIM_PATIENT ADD COLUMN IF NOT EXISTS gender STRING"
    )
    cursor.execute(
        "ALTER TABLE GOLD.DIM_PATIENT ADD COLUMN IF NOT EXISTS valid_from DATE"
    )
    cursor.execute(
        "ALTER TABLE GOLD.DIM_PATIENT ADD COLUMN IF NOT EXISTS valid_to DATE"
    )
    cursor.execute(
        "ALTER TABLE GOLD.DIM_PATIENT ADD COLUMN IF NOT EXISTS is_current BOOLEAN"
    )

    cursor.execute(
        "ALTER TABLE GOLD.FACT_TREATMENT ADD COLUMN IF NOT EXISTS patient_sk NUMBER"
    )
    cursor.execute(
        "ALTER TABLE GOLD.FACT_TREATMENT ADD COLUMN IF NOT EXISTS hospital_sk NUMBER"
    )
    cursor.execute(
        "ALTER TABLE GOLD.FACT_TREATMENT ADD COLUMN IF NOT EXISTS disease_sk NUMBER"
    )
    cursor.execute(
        (
            "ALTER TABLE GOLD.FACT_TREATMENT "
            "ADD COLUMN IF NOT EXISTS admission_date_sk NUMBER"
        )
    )
    cursor.execute(
        (
            "ALTER TABLE GOLD.FACT_TREATMENT "
            "ADD COLUMN IF NOT EXISTS discharge_date_sk NUMBER"
        )
    )
    cursor.execute(
        "ALTER TABLE GOLD.FACT_TREATMENT ADD COLUMN IF NOT EXISTS patient_id NUMBER"
    )
    cursor.execute(
        (
            "ALTER TABLE GOLD.FACT_TREATMENT "
            "ADD COLUMN IF NOT EXISTS treatment_cost NUMBER(18, 2)"
        )
    )
    cursor.execute(
        "ALTER TABLE GOLD.FACT_TREATMENT ADD COLUMN IF NOT EXISTS stay_days NUMBER"
    )
    cursor.execute(
        "ALTER TABLE GOLD.FACT_TREATMENT ADD COLUMN IF NOT EXISTS batch_date DATE"
    )
    cursor.execute(
        (
            "ALTER TABLE GOLD.FACT_TREATMENT "
            "ADD COLUMN IF NOT EXISTS inserted_at TIMESTAMP_NTZ"
        )
    )

    cursor.execute(
        (
            "ALTER TABLE GOLD.DAILY_SUMMARY_REPORT "
            "ADD COLUMN IF NOT EXISTS total_rows_processed NUMBER"
        )
    )
    cursor.execute(
        (
            "ALTER TABLE GOLD.DAILY_SUMMARY_REPORT "
            "ADD COLUMN IF NOT EXISTS total_treatment_cost NUMBER(18, 2)"
        )
    )
    cursor.execute(
        (
            "ALTER TABLE GOLD.DAILY_SUMMARY_REPORT "
            "ADD COLUMN IF NOT EXISTS avg_stay_days NUMBER(18, 2)"
        )
    )
    cursor.execute(
        (
            "ALTER TABLE GOLD.DAILY_SUMMARY_REPORT "
            "ADD COLUMN IF NOT EXISTS unique_patients NUMBER"
        )
    )
    cursor.execute(
        (
            "ALTER TABLE GOLD.DAILY_SUMMARY_REPORT "
            "ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP_NTZ"
        )
    )

    # Backfill surrogate keys for legacy rows where PK columns were absent.
    cursor.execute(
        """
        UPDATE GOLD.DIM_HOSPITAL t
        SET hospital_sk = s.new_sk
        FROM (
            SELECT
                hospital_name,
                ROW_NUMBER() OVER (ORDER BY hospital_name) AS new_sk
            FROM GOLD.DIM_HOSPITAL
            WHERE hospital_sk IS NULL
        ) s
        WHERE t.hospital_name = s.hospital_name
          AND t.hospital_sk IS NULL
        """
    )

    cursor.execute(
        """
        UPDATE GOLD.DIM_DISEASE t
        SET disease_sk = s.new_sk
        FROM (
            SELECT
                disease_name,
                ROW_NUMBER() OVER (ORDER BY disease_name) AS new_sk
            FROM GOLD.DIM_DISEASE
            WHERE disease_sk IS NULL
        ) s
        WHERE t.disease_name = s.disease_name
          AND t.disease_sk IS NULL
        """
    )

    cursor.execute(
        """
        UPDATE GOLD.DIM_DATE t
        SET date_sk = s.new_sk
        FROM (
            SELECT
                date_value,
                ROW_NUMBER() OVER (ORDER BY date_value) AS new_sk
            FROM GOLD.DIM_DATE
            WHERE date_sk IS NULL
        ) s
        WHERE t.date_value = s.date_value
          AND t.date_sk IS NULL
        """
    )

    cursor.execute(
        """
        UPDATE GOLD.DIM_PATIENT t
        SET patient_sk = s.new_sk
        FROM (
            SELECT
                patient_id,
                patient_name,
                valid_from,
                ROW_NUMBER() OVER (
                    ORDER BY
                        COALESCE(patient_id, 0),
                        COALESCE(valid_from, TO_DATE('1900-01-01'))
                ) AS new_sk
            FROM GOLD.DIM_PATIENT
            WHERE patient_sk IS NULL
        ) s
        WHERE COALESCE(t.patient_id, -1) = COALESCE(s.patient_id, -1)
          AND COALESCE(t.patient_name, '') = COALESCE(s.patient_name, '')
          AND COALESCE(t.valid_from, TO_DATE('1900-01-01')) =
              COALESCE(s.valid_from, TO_DATE('1900-01-01'))
          AND t.patient_sk IS NULL
        """
    )


def _merge_dimensions(cursor, run_date: str) -> None:
    cursor.execute(
        """
        MERGE INTO GOLD.DIM_HOSPITAL t
        USING (
            SELECT DISTINCT hospital
            FROM SILVER.PATIENT_CLEAN
            WHERE batch_date = %s::DATE
        ) s
        ON t.hospital_name = s.hospital
        WHEN NOT MATCHED THEN
            INSERT (hospital_name)
            VALUES (s.hospital)
        """,
        (run_date,),
    )

    cursor.execute(
        """
        MERGE INTO GOLD.DIM_DISEASE t
        USING (
            SELECT DISTINCT disease
            FROM SILVER.PATIENT_CLEAN
            WHERE batch_date = %s::DATE
        ) s
        ON t.disease_name = s.disease
        WHEN NOT MATCHED THEN
            INSERT (disease_name)
            VALUES (s.disease)
        """,
        (run_date,),
    )

    cursor.execute(
        """
        MERGE INTO GOLD.DIM_DATE t
        USING (
            SELECT DISTINCT admission_date AS dt
            FROM SILVER.PATIENT_CLEAN
            WHERE batch_date = %s::DATE
            UNION
            SELECT DISTINCT discharge_date AS dt
            FROM SILVER.PATIENT_CLEAN
            WHERE batch_date = %s::DATE
        ) s
        ON t.date_value = s.dt
        WHEN NOT MATCHED THEN
            INSERT (
                date_value,
                day_of_week,
                month_num,
                quarter_num,
                year_num
            )
            VALUES (
                s.dt,
                DAYOFWEEKISO(s.dt),
                MONTH(s.dt),
                QUARTER(s.dt),
                YEAR(s.dt)
            )
        """,
        (run_date, run_date),
    )


def _apply_scd2_patient(cursor, run_date: str) -> None:
    # Expire current records that changed.
    cursor.execute(
        """
        UPDATE GOLD.DIM_PATIENT t
        SET is_current = FALSE,
            valid_to = %s::DATE
        FROM (
            SELECT DISTINCT
                patient_id,
                patient_name,
                age,
                gender
            FROM SILVER.PATIENT_CLEAN
            WHERE batch_date = %s::DATE
        ) s
        WHERE t.patient_id = s.patient_id
          AND t.is_current = TRUE
          AND (
              COALESCE(t.patient_name, '') <> COALESCE(s.patient_name, '')
              OR COALESCE(t.age, -1) <> COALESCE(s.age, -1)
              OR COALESCE(t.gender, '') <> COALESCE(s.gender, '')
          )
        """,
        (run_date, run_date),
    )

    # Insert first-time and changed rows as new current versions.
    cursor.execute(
        """
        INSERT INTO GOLD.DIM_PATIENT (
            patient_sk,
            patient_id,
            patient_name,
            age,
            gender,
            valid_from,
            valid_to,
            is_current
        )
        SELECT
            COALESCE((SELECT MAX(patient_sk) FROM GOLD.DIM_PATIENT), 0)
            + ROW_NUMBER() OVER (ORDER BY s.patient_id, s.patient_name) AS patient_sk,
            s.patient_id,
            s.patient_name,
            s.age,
            s.gender,
            %s::DATE AS valid_from,
            TO_DATE('9999-12-31') AS valid_to,
            TRUE AS is_current
        FROM (
            SELECT DISTINCT
                patient_id,
                patient_name,
                age,
                gender
            FROM SILVER.PATIENT_CLEAN
            WHERE batch_date = %s::DATE
        ) s
        LEFT JOIN GOLD.DIM_PATIENT t
          ON t.patient_id = s.patient_id
         AND t.is_current = TRUE
        WHERE t.patient_id IS NULL
           OR (
               COALESCE(t.patient_name, '') <> COALESCE(s.patient_name, '')
               OR COALESCE(t.age, -1) <> COALESCE(s.age, -1)
               OR COALESCE(t.gender, '') <> COALESCE(s.gender, '')
           )
        """,
        (run_date, run_date),
    )


def _load_fact_table(cursor, run_date: str) -> None:
    cursor.execute(
        "DELETE FROM GOLD.FACT_TREATMENT WHERE batch_date = %s::DATE", (run_date,)
    )

    cursor.execute(
        """
        INSERT INTO GOLD.FACT_TREATMENT (
            patient_sk,
            hospital_sk,
            disease_sk,
            admission_date_sk,
            discharge_date_sk,
            patient_id,
            treatment_cost,
            stay_days,
            batch_date,
            inserted_at
        )
        SELECT
            dp.patient_sk,
            dh.hospital_sk,
            dd.disease_sk,
            da.date_sk AS admission_date_sk,
            dd2.date_sk AS discharge_date_sk,
            s.patient_id,
            s.treatment_cost,
            s.stay_days,
            s.batch_date,
            CURRENT_TIMESTAMP()
        FROM SILVER.PATIENT_CLEAN s
        JOIN GOLD.DIM_PATIENT dp
          ON dp.patient_id = s.patient_id
         AND dp.is_current = TRUE
        JOIN GOLD.DIM_HOSPITAL dh
          ON dh.hospital_name = s.hospital
        JOIN GOLD.DIM_DISEASE dd
          ON dd.disease_name = s.disease
        JOIN GOLD.DIM_DATE da
          ON da.date_value = s.admission_date
        JOIN GOLD.DIM_DATE dd2
          ON dd2.date_value = s.discharge_date
        WHERE s.batch_date = %s::DATE
        """,
        (run_date,),
    )


def _upsert_daily_summary(cursor, run_date: str) -> None:
    cursor.execute(
        """
        MERGE INTO GOLD.DAILY_SUMMARY_REPORT t
        USING (
            SELECT
                %s::DATE AS report_date,
                COUNT(*) AS total_rows_processed,
                COALESCE(SUM(treatment_cost), 0) AS total_treatment_cost,
                COALESCE(AVG(stay_days), 0) AS avg_stay_days,
                COUNT(DISTINCT patient_id) AS unique_patients
            FROM GOLD.FACT_TREATMENT
            WHERE batch_date = %s::DATE
        ) s
        ON t.report_date = s.report_date
        WHEN MATCHED THEN UPDATE SET
            total_rows_processed = s.total_rows_processed,
            total_treatment_cost = s.total_treatment_cost,
            avg_stay_days = s.avg_stay_days,
            unique_patients = s.unique_patients,
            updated_at = CURRENT_TIMESTAMP()
        WHEN NOT MATCHED THEN INSERT (
            report_date,
            total_rows_processed,
            total_treatment_cost,
            avg_stay_days,
            unique_patients,
            updated_at
        )
        VALUES (
            s.report_date,
            s.total_rows_processed,
            s.total_treatment_cost,
            s.avg_stay_days,
            s.unique_patients,
            CURRENT_TIMESTAMP()
        )
        """,
        (run_date, run_date),
    )


def build_gold_layer(run_date: str) -> None:
    """Build/refresh Gold dimensions, fact, and summary report.

    Args:
        run_date: Pipeline batch date (`YYYY-MM-DD`).
    """
    conn = get_connection(schema="GOLD")
    cursor = conn.cursor()

    try:
        _ensure_gold_tables(cursor)
        _merge_dimensions(cursor, run_date)
        _apply_scd2_patient(cursor, run_date)
        _load_fact_table(cursor, run_date)
        _upsert_daily_summary(cursor, run_date)
        conn.commit()
        print(f"Gold layer built successfully for {run_date}")
    finally:
        cursor.close()
        conn.close()
