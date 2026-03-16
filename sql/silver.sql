CREATE SCHEMA IF NOT EXISTS SILVER;

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
);
