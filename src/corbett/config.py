import os

try:
    import dotenv
    dotenv.load_dotenv()
except ImportError:
    pass

_default_env = 'test'
_default_region = 'us-east-1'
_base_connection_table_name = '{env}-Connections'

# TODO: update these to use the custom domain names
_execute_hosts = {
    'prod': 'https://7o9fmj3s42.execute-api.{region}.amazonaws.com/Prod',
    'test': 'https://wg9weyic1j.execute-api.{region}.amazonaws.com/Prod',
    'staging': 'https://sxdcoyd9l5.execute-api.{region}.amazonaws.com/Prod',
    'dev': 'https://wg9weyic1j.execute-api.{region}.amazonaws.com/Prod'
}
_api_hosts ={
    'prod': 'https://api.corbettapp.com',
    'staging': 'https://api-staging.corbettapp.com',
    'test': 'https://api-test.corbettapp.com',
    'dev': 'https://api-dev.corbettapp.com:5000'
}
_namespaces = {
    'dev':'corbett_dev',
    'staging': 'corbett_staging',
    'test': 'corbett_test',
    'prod': 'corbett'
}


env = os.environ.get('CORBETT_ENV', _default_env)
region = os.environ.get('CORBETT_REGION', _default_region)
snowflake_namespace = _namespaces[env]
snowflake_api_integration = _namespaces[env]
api_host = _api_hosts[env]
api_aws_role_arn = f'arn:aws:iam::573390937803:role/{env}-SnowflakePublicRole'
execute_host = _execute_hosts[env].format(region=region)
connection_table_name = _base_connection_table_name.format(env=env)
secrets_arn = os.environ.get('SECRETS_ARN')