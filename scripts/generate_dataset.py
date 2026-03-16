"""Generate synthetic healthcare patient dataset for pipeline testing."""

from __future__ import annotations

import os
import random

import pandas as pd
from faker import Faker

DISEASES = ["Diabetes", "Asthma", "Cancer", "Hypertension", "Heart Disease"]
HOSPITALS = ["Norvic Hospital", "Grande Hospital", "KMC Hospital", "Bir Hospital"]
NUM_RECORDS = 1000


def generate_patient_data(num_records: int = NUM_RECORDS) -> pd.DataFrame:
    """Generate synthetic patient records.

    Args:
        num_records: Number of patient records to generate.

    Returns:
        DataFrame containing synthetic healthcare patient data.
    """
    fake = Faker()
    rows = []

    for i in range(num_records):
        admission = fake.date_between(start_date="-1y", end_date="today")
        discharge = fake.date_between(start_date=admission, end_date="today")

        rows.append(
            {
                "patient_id": i + 1,
                "patient_name": fake.name(),
                "age": random.randint(20, 80),
                "gender": random.choice(["M", "F"]),
                "hospital": random.choice(HOSPITALS),
                "disease": random.choice(DISEASES),
                "admission_date": admission,
                "discharge_date": discharge,
                "treatment_cost": random.randint(200, 5000),
            }
        )

    return pd.DataFrame(rows)


def main() -> None:
    """Entry point: generate dataset and write to data/patient_data.csv."""
    df = generate_patient_data()

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_path = os.path.join(project_root, "data", "patient_data.csv")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Dataset generated: {len(df)} rows at {output_path}")


if __name__ == "__main__":
    main()
