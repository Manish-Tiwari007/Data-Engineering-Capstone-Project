from snowflake_connection import get_connection

def build_gold_layer():

    conn = get_connection()
    cursor = conn.cursor()

    query = """
    INSERT INTO GOLD.DIM_HOSPITAL (hospital_name)
    SELECT DISTINCT hospital
    FROM SILVER.PATIENT_CLEAN
    """

    cursor.execute(query)

    conn.close()

    print("Gold layer built")