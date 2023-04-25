from .app import DebuggerApp
from .credentials import get_credentials


def handler(event, context):
    credentials = get_credentials()
    app = DebuggerApp()
    return app.invoke(event, context, credentials)
