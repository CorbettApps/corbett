# Corbett

_Query your Google Sheets data from Snowflake_

```sql
select *
from table(corbett.gsheets.sheet(
    '1Z2Uhf...',  -- The spreadsheet ID
    'A1:B6',      -- The range of cells to query,
    30            -- The number of rows to include
))
```

Corbett provides a Snowflake [external function](https://docs.snowflake.com/en/sql-reference/external-functions-introduction#what-is-an-external-function) that enables directly querying data from a Google Sheet.

The data from the Spreadsheet is queried in real time, so updates to the sheet are immediately reflected the next time the query is ran.

## Install

Download the installer from PyPI.

```bash
pip install corbett
```

Create an account.

```bash
corbett register
```

Set environment variables to enable the installer to authenticate with your Snowflake account. Note that you must use the `accountadmin` role in order to run the installer.

```bash
export SNOWSQL_ROLE='accountadmin'
export SNOWSQL_USER='...'
export SNOWSQL_PWD='...'
export SNOWSQL_ACCOUNT='...'
```

Run the installer. You will be prompted to open a link and approve Corbett's access to your Google Sheets.

```
corbett install gsheets
```

## Requesting help

Please open an issue in this repository if you run into any problems installing or using the function.
