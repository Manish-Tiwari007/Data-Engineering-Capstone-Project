CREATE SCHEMA IF NOT EXISTS BRONZE;

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
);
