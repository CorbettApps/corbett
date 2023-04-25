import json
from pydantic import BaseModel


class AppMethod(BaseModel):
    args: list
    return_type: str

    def format_args(self):
        return ", ".join([f"{arg_name} {arg_type}" for arg_name, arg_type in self.args])

    def call(self, event, context, credentials):
        raise NotImplementedError


class App(BaseModel):
    name: str
    functions = dict()

    # TODO: invoke should load a `Connection` object instead of receiving the decrypted credentials.
    # It can then validate the API Key Hash from the connection against the API Key provided
    # by the event, and also decrypt the credentials and pass them to the function.
    def invoke(self, event, context, credentials):
        if "path" not in event:
            raise Exception("Not a resource")

        try:
            _, app_name, app_method = event["path"].split("/")[:3]
        except Exception as err:
            raise Exception(f"Bad resource definition: {str(err)}")

        if app_name != self.name:
            raise Exception("Unexpected app_name for App {self.name}: {app_name}")

        if app_method not in self.functions:
            raise AttributeError(
                f"{self.__class__.__name__} has no method {app_method}"
            )
        else:
            method = self.functions[app_method]
            body, status_code = method.call(event, context, credentials)
            return {
                "isBase64Encoded": False,
                "statusCode": status_code,
                "body": json.dumps(body),
            }

    def handle_create_request(self, connection, request):
        """
        Called by the api after a connection is created. Should return a dictionary
        with additional parameters to include in the response to POST /app. For an
        OAuth app this can generate the OAuth Authorization request URL.
        """
        raise NotImplementedError

    def handle_create_response(self, client, response):
        """
        Called by the installer after POST /apps. For an oauth app, it should open
        the OAuth Authorization Request URL provided by the api, and then poll to
        wait for the user to finish the oauth flow.
        """
        raise NotImplementedError
