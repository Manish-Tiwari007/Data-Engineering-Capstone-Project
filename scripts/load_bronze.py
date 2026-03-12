from snowflake_connection import get_connection

def load_to_bronze(df):

    conn = get_connection()

    cursor = conn.cursor()

    for _, row in df.iterrows():

        query = f"""
        INSERT INTO PATIENT_RAW
        VALUES (
        {row.patient_id},
        '{row.patient_name}',
        {row.age},
        '{row.gender}',
        '{row.hospital}',
        '{row.disease}',
        '{row.admission_date}',
        '{row.discharge_date}',
        {row.treatment_cost},
        CURRENT_TIMESTAMP
        )
        """

        cursor.execute(query)

    conn.close()