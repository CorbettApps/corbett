import json
from corbett import App, AppMethod


gsheet_table_func_template = """
create or replace function {namespace}.{app_name}.sheet(
    spreadsheet_id varchar,
    cell_range varchar,
    max_rows int
)
returns table ( sheet variant )
as
$$
with result as (
select
    {namespace}.{app_name}._sheet(
        spreadsheet_id,
        cell_range,
        -1 + row_number() over (order by 1)
    ) as sheet
from table(generator(rowcount=>max_rows))
)
select *
from result
where sheet is not null
$$
"""


class GsheetsSheetMethod(AppMethod):
    args = [("spreadsheet_id", "varchar"), ("cells", "varchar"), ("rownum", "integer")]
    return_type = "variant"

    def call(self, event, context, credentials):
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build

        token = credentials["token"]
        refresh_token = credentials["refresh_token"]
        client_id = credentials["client_id"]
        token_uri = credentials["token_uri"]
        client_secret = credentials["client_secret"]
        scopes = credentials["scopes"]
        creds = Credentials(
            token=token,
            refresh_token=refresh_token,
            client_id=client_id,
            client_secret=client_secret,
            token_uri=token_uri,
            scopes=scopes,
        )

        if creds.expired:
            creds.refresh(Request)

        service = build("sheets", "v4", credentials=creds)
        sheet = service.spreadsheets()

        rows_requested = json.loads(event["body"])["data"]
        spreadsheet_id, sheet_range = rows_requested[0][1:3]
        result = (
            sheet.values()
            .get(spreadsheetId=spreadsheet_id, range=sheet_range)
            .execute()
        )
        values = result.get("values", [])
        headers = values.pop(0)

        result = []
        for row in rows_requested:
            # The first element of the array is the position in the batch - NOT the position overall. In other
            # words, when we receive two batches, they both contain "row 0". So we include a separate
            # argument in the table function which is the _actual_ row requested, ie it passes row_number()
            # as the last argument in the function. The spreadsheet id and the cell range are the
            # 2nd and 3rd arguments.
            row_requested = row.pop(-1)
            if row_requested >= len(values):
                data = None
            else:
                data = dict(zip(headers, values[row_requested]))
            result.append([row_requested, data])
        return {"data": result}, 200


class GsheetsApp(App):
    name: str = "gsheets"
    functions = {
        "_sheet": GsheetsSheetMethod(),
    }
    extras = {"sheet": gsheet_table_func_template}

    def handle_create_request(self, connection, request):
        return {"debugging": True}

    # This needs to request the oauth URL from the api to start the OAuth
    # request
    def handle_create_response(self, client, response):
        app_response = client.get_app(response["app_id"])
        app_details = app_response.json()

        exists = app_response.status_code == 200
        if not exists:
            raise Exception(f"Error: {app_details}")
        resp = client.send(
            "GET", "/oauth/gsheets/url", json={"app_id": response["app_id"]}
        )
        print(resp.json())
