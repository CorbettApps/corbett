from corbett import App
from corbett import config
from .snowflake import get_conn
from .client import Client



create_database_template = """
create database if not exists {namespace}
"""

create_api_integration_template = """
create api integration if not exists {namespace} with
    enabled = true
    api_provider = aws_api_gateway
    api_key = '{api_key}'
    api_aws_role_arn = '{api_aws_role_arn}'
    api_allowed_prefixes = ('{execute_host}')
"""

create_app_schema_template = """
create or replace schema {namespace}.{app_name}
"""

create_app_method_template = """
create or replace external function {namespace}.{app_name}.{app_method}({formatted_args})
returns {return_type}
api_integration = {namespace}
headers = (
    'corbett-user-id' = '{user_id}',
    'corbett-app-id' = '{app_id}'
)
context_headers = (
    current_account
)
as '{host}/{app_name}/{app_method}'
"""


class InstallationStatement:
    def __init__(self, template, params=None):
        self.template = template
        self.params = params

    def render(self):
        params = self.params or dict()
        return self.template.format(**params)


class Installer:
    def __init__(self, app: App, client: Client, verbose=False):
        self.app = app
        self.verbose = verbose
        self.client = client
    
    def get_app_registration(self):
        resp = self.client.register_app(app_type=self.app.name)
        if not resp.ok:
            raise Exception(f"Error registering app: {resp.content.decode()}")
        return resp.json()

    def get_create_database_statement(self):
        return InstallationStatement(template=create_database_template, params={
            'namespace': config.snowflake_namespace,
        })
    
    def get_create_api_integration_statement(self):
        resp = self.client.api_key()
        if not resp.ok:
            raise Exception(f"Error retrieving api key: {resp.json()}")
        else:
            api_key = resp.json()['api_key_value']
        return InstallationStatement(template=create_api_integration_template, params={
            'api_aws_role_arn': config.api_aws_role_arn,
            'execute_host': config.execute_host,
            'namespace': config.snowflake_namespace,
            'api_key': api_key
        })
    
    def get_create_app_schema_statemnt(self):
        return InstallationStatement(template=create_app_schema_template, params={
            'app_name': self.app.name,
            'namespace': config.snowflake_namespace,
        })

    def run(self, dry_run=True):
        app_registration = self.get_app_registration()
        try:
            self.app.handle_create_response(client=self.client, response=app_registration)
        except NotImplementedError:
            pass

        conn = get_conn()
        cursor = conn.cursor()
        stmts = [
            self.get_create_database_statement(),
            self.get_create_api_integration_statement(),
            self.get_create_app_schema_statemnt(),
        ]

        for function_name, function in self.app.functions.items():
            stmts.append(InstallationStatement(template=create_app_method_template, params={
                'app_method': function_name,
                'app_name': self.app.name,
                'namespace': config.snowflake_namespace,
                'host': config.execute_host,
                'user_id': app_registration['user_id'],
                'app_id': app_registration['app_id'],
                'formatted_args': function.format_args(),
                'return_type': function.return_type
            }))
        
        for extra_name, extra_template in self.app.extras.items():
            stmts.append(InstallationStatement(template=extra_template, params={
                'app_name': self.app.name,
                'namespace': config.snowflake_namespace
            }))

        for stmt in stmts:
            command = stmt.render()
            if self.verbose or dry_run:
                print(command)
            if not dry_run:
                resp = cursor.execute(command)
                print(resp)
