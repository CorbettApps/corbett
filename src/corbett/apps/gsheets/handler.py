from .app import GsheetsApp
from .credentials import get_credentials


def handler(event, context):
    credentials = get_credentials(event=event, context=context)
    app = GsheetsApp()
    return app.invoke(event=event, context=context, credentials=credentials)
