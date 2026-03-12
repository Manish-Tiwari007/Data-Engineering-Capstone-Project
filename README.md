# Healthcare Data Engineering Capstone Project

A end-to-end data engineering pipeline that ingests, transforms, and models healthcare patient data using Apache Airflow, Snowflake, and Docker — following a **Bronze → Silver → Gold** medallion architecture.

---

## Architecture Overview

```
CSV File (Source)
      │
      ▼
┌─────────────┐
│   BRONZE    │  Raw ingestion — PATIENT_RAW table in Snowflake
└─────────────┘
      │
      ▼
┌─────────────┐
│   SILVER    │  Cleaned & transformed — PATIENT_CLEAN table
└─────────────┘
      │
      ▼
┌─────────────┐
│    GOLD     │  Star schema — DIM/FACT tables for analytics
└─────────────┘
```

---

## Tech Stack

| Tool | Purpose |
|------|---------|
| Apache Airflow 2.7.1 | Pipeline orchestration |
| Snowflake | Cloud data warehouse |
| PostgreSQL 13 | Airflow metadata database |
| Docker & Docker Compose | Containerized deployment |
| Python 3.8 | ETL scripting |
| Pandas | Data manipulation |
| pre-commit (black + flake8) | Code quality enforcement |

---

## Project Structure

```
├── dags/
│   └── healthcare_pipeline_dag.py   # Airflow DAG definition
├── scripts/
│   ├── extract.py                   # Reads patient_data.csv
│   ├── load_bronze.py               # Loads raw data to Snowflake Bronze
│   ├── transform_silver.py          # Cleans and transforms to Silver
│   ├── build_gold.py                # Builds Star Schema in Gold layer
│   ├── snowflake_connection.py      # Snowflake connector
│   └── generate_dataset.py          # Synthetic data generator (1000 patients)
├── sql/
│   ├── bronze.sql                   # Bronze layer DDL
│   ├── silver.sql                   # Silver layer DDL
│   └── gold.sql                     # Gold layer DDL
├── data/
│   └── patient_data.csv             # Generated healthcare dataset
├── docker-compose.yml               # Airflow + PostgreSQL services
├── requirement.txt                  # Python dependencies
└── .pre-commit-config.yaml          # black + flake8 hooks
```

---

## Pipeline DAG

The DAG `healthcare_data_pipeline` runs daily with 4 sequential tasks:

```
extract_data → load_bronze → transform_silver → build_gold
```

| Task | Description |
|------|-------------|
| `extract_data` | Reads `patient_data.csv` from `/opt/airflow/data/` |
| `load_bronze` | Inserts raw records into `BRONZE.PATIENT_RAW` in Snowflake |
| `transform_silver` | Cleans data and computes `stay_days`, loads to `SILVER.PATIENT_CLEAN` |
| `build_gold` | Populates `GOLD.DIM_HOSPITAL` from distinct hospital values |

---

## Snowflake Schema

### Bronze — Raw Layer
```sql
BRONZE.PATIENT_RAW (
    patient_id, patient_name, age, gender,
    hospital, disease, admission_date,
    discharge_date, treatment_cost, ingested_at
)
```

### Silver — Cleaned Layer
```sql
SILVER.PATIENT_CLEAN (
    patient_id, patient_name, age, gender,
    hospital, disease, admission_date,
    discharge_date, stay_days, treatment_cost
)
```

### Gold — Star Schema
```
GOLD.DIM_HOSPITAL    — Hospital dimension
GOLD.DIM_PATIENT     — Patient dimension
GOLD.DIM_DISEASE     — Disease dimension
GOLD.DIM_DATE        — Date dimension
GOLD.FACT_TREATMENT  — Treatment fact table
```

---

## Getting Started

### Prerequisites
- Docker Desktop installed and running
- Snowflake account with `MBUST_MDS_03` database and Bronze/Silver/Gold schemas created

### 1. Clone the repository
```bash
git clone https://github.com/Manish-Tiwari007/Data-Engineering-Capstone-Project.git
cd Data-Engineering-Capstone-Project
```

### 2. Generate the dataset
```bash
pip install pandas faker
python scripts/generate_dataset.py
```

### 3. Start Airflow with Docker
```bash
docker compose up -d
```

Wait ~30 seconds, then open: `http://localhost:8080`

- **Username:** `admin`
- **Password:** `admin`

### 4. Trigger the pipeline
- Find `healthcare_data_pipeline` in the Airflow UI
- Enable the toggle
- Click the **Play** button to trigger manually

---

## Dataset

Synthetic healthcare data generated using the `Faker` library — 1000 patient records with the following fields:

| Field | Description |
|-------|-------------|
| patient_id | Unique patient identifier |
| patient_name | Full name |
| age | Age (20–80) |
| gender | M / F |
| hospital | One of 4 Nepali hospitals |
| disease | One of 5 diseases |
| admission_date | Admission date |
| discharge_date | Discharge date |
| treatment_cost | Cost in USD (200–5000) |

---

## Dependencies

```
pandas
snowflake-connector-python
apache-airflow
```

Install locally:
```bash
pip install -r requirement.txt
```

---

## Code Quality

This project uses `pre-commit` hooks to enforce code style:

```bash
pre-commit install
pre-commit run --all-files
```

Hooks configured:
- **black** — code formatter
- **flake8** — linting

---

## Author

**Manish Tiwari**
- Snowflake: `ACCOUNTADMIN` | Account: `LUTCNGF-FUB28409`
- GitHub: [Manish-Tiwari007](https://github.com/Manish-Tiwari007)
