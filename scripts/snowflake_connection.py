import snowflake.connector

def get_connection():

    conn = snowflake.connector.connect(
        user="MANISH",
        password="Learn@snowflake01",
        account="LUTCNGF-FUB28409",
        warehouse="COMPUTE_WH",
        database="MBUST_MDS_03",
        schema="BRONZE"
    )

    return conn