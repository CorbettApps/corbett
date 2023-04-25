import json
from cryptography.fernet import Fernet
from json.decoder import JSONDecodeError
from corbett import App, AppMethod
from corbett.models import Connection


class DebuggerHealthcheckMethod(AppMethod):
    args = []
    return_type = 'variant'

    def call(self, event, context, credentials):
        rows = [
            [ 0, {"healthy": True} ]
        ]
        return { "data": rows }, 200


class DebuggerWhoamiMethod(AppMethod):
    args = []
    return_type = 'variant'

    def call(self, event, context, credentials):
        user_id = event['headers']['sf-custom-corbett-user-id']
        app_id = event['headers']['sf-custom-corbett-app-id']
        account = event['headers']['sf-context-current-account']
        api_key = event['headers']['x-api-key']
        print(f"Invoke debugger.whoami with user_id={user_id} app_id={app_id} account={account} region={Connection.Meta.region}")
        try:
            conn = Connection.get(user_id, app_id)
            verified = conn.check_api_key(api_key)
        except:
            verified = False
        rows = [
            [0, {'user_id': user_id, 'app_id': app_id, 'account': account, 'verified': verified}]
        ]
        return {"data": rows}, 200


class DebuggerEchoMethod(AppMethod):
    # The order matters here, as these are not keyword arguments
    args = [
        ('hello', 'varchar'),
        ('world', 'varchar')
    ]
    return_type = 'array'
    
    def call(self, event, context, credentials):
        inputs = json.loads(event['body'])['data']
        rows = []
        for row in inputs:
            rows.append([row[0], row[1:]])
        return { "data": rows }, 200    


class DebuggerApp(App):
    name: str = "debugger"
    functions = {
        'healthcheck': DebuggerHealthcheckMethod(),
        'whoami': DebuggerWhoamiMethod(),
        'echo': DebuggerEchoMethod()
    }

    def handle_create_request(self, connection, request):
        return {'debugging': True}
    
    # This needs to request the oauth URL from the api, we can use the
    # google client libraries to generate the URL
    def handle_create_response_tmp(self, client, response):
        params = response['params']
        app_response = client.get_app(response['app_id'])
        app_details = app_response.json()
        exists = app_response.status_code == 200
        if not exists:
            print(f"Error: {app_details}")
        else:
            print(f"Created app {app_details['app_id']} with params {params}")
