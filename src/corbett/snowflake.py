import os
import snowflake.connector


def get_conn():
    user = os.environ['SNOWSQL_USER']
    password = os.environ['SNOWSQL_PWD']
    warehouse = os.environ.get('SNOWSQL_WAREHOUSE')
    account = os.environ['SNOWSQL_ACCOUNT']
    role = os.environ['SNOWSQL_ROLE']
    return snowflake.connector.connect(
        user=user,
        password=password,
        warehouse=warehouse,
        account=account,
        role=role
    )