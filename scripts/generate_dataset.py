import pandas as pd
import random
import os
from faker import Faker

fake = Faker()

diseases = ["Diabetes","Asthma","Cancer","Hypertension","Heart Disease"]
hospitals = ["Norvic Hospital","Grande Hospital","KMC Hospital","Bir Hospital"]

rows = []

for i in range(1000):

    admission = fake.date_between(start_date="-1y", end_date="today")
    discharge = fake.date_between(start_date=admission, end_date="today")

    rows.append({

        "patient_id": i+1,
        "patient_name": fake.name(),
        "age": random.randint(20,80),
        "gender": random.choice(["M","F"]),
        "hospital": random.choice(hospitals),
        "disease": random.choice(diseases),
        "admission_date": admission,
        "discharge_date": discharge,
        "treatment_cost": random.randint(200,5000)

    })

df = pd.DataFrame(rows)

# Use absolute path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
output_path = os.path.join(project_root, "data", "patient_data.csv")

df.to_csv(output_path, index=False)

print(f"Dataset generated at {output_path}")