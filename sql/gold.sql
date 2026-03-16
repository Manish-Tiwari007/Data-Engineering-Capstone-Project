CREATE SCHEMA IF NOT EXISTS GOLD;

CREATE TABLE IF NOT EXISTS GOLD.DIM_HOSPITAL (
	hospital_sk NUMBER AUTOINCREMENT,
	hospital_name STRING,
	CONSTRAINT PK_DIM_HOSPITAL PRIMARY KEY (hospital_sk)
);

CREATE TABLE IF NOT EXISTS GOLD.DIM_DISEASE (
	disease_sk NUMBER AUTOINCREMENT,
	disease_name STRING,
	CONSTRAINT PK_DIM_DISEASE PRIMARY KEY (disease_sk)
);

CREATE TABLE IF NOT EXISTS GOLD.DIM_DATE (
	date_sk NUMBER AUTOINCREMENT,
	date_value DATE,
	day_of_week NUMBER,
	month_num NUMBER,
	quarter_num NUMBER,
	year_num NUMBER,
	CONSTRAINT PK_DIM_DATE PRIMARY KEY (date_sk)
);

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
);

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
);

CREATE TABLE IF NOT EXISTS GOLD.DAILY_SUMMARY_REPORT (
	report_date DATE,
	total_rows_processed NUMBER,
	total_treatment_cost NUMBER(18, 2),
	avg_stay_days NUMBER(18, 2),
	unique_patients NUMBER,
	updated_at TIMESTAMP_NTZ,
	CONSTRAINT PK_DAILY_SUMMARY PRIMARY KEY (report_date)
);

-- Configure and run this after setting your notification integration.
-- CREATE OR REPLACE ALERT GOLD.ALERT_DAILY_SUMMARY
--   WAREHOUSE = COMPUTE_WH
--   SCHEDULE = 'USING CRON 0 8 * * * Asia/Kathmandu'
--   IF (EXISTS(
--       SELECT 1
--       FROM GOLD.DAILY_SUMMARY_REPORT
--       WHERE report_date = CURRENT_DATE()
--   ))
--   THEN
--   CALL SYSTEM$SEND_EMAIL(
--       'YOUR_NOTIFICATION_INTEGRATION_NAME',
--       'stakeholder@example.com',
--       'Daily Healthcare Pipeline Summary',
--       (SELECT
--           'Rows: ' || total_rows_processed ||
--           ', Total Cost: ' || total_treatment_cost ||
--           ', Avg Stay: ' || avg_stay_days
--        FROM GOLD.DAILY_SUMMARY_REPORT
--        WHERE report_date = CURRENT_DATE())
--   );
