from snowflake_connection import get_connection

def transform_to_silver():

    conn = get_connection()
    cursor = conn.cursor()

    query = """
    INSERT INTO SILVER.PATIENT_CLEAN

    SELECT
    patient_id,
    patient_name,
    age,
    gender,
    hospital,
    disease,
    admission_date,
    discharge_date,
    DATEDIFF(day, admission_date, discharge_date) AS stay_days,
    treatment_cost

    FROM BRONZE.PATIENT_RAW
    """

    cursor.execute(query)

    conn.close()

    print("Data moved to Silver layer")