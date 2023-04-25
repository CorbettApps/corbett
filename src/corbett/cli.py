import os
import json
from dotenv import load_dotenv
import click
from snowflake.connector import DictCursor
from click import Group, option, argument
import corbett.config as config
from .apps.debugger import DebuggerApp
from .apps.gsheets import GsheetsApp
from .snowflake import get_conn
from .client import Client
from .installer import Installer
from .version import version


load_dotenv()


def save_jwt(token: dict):
    home = os.path.join(os.path.expanduser("~"), ".corbett")
    os.makedirs(home, exist_ok=True)
    token_filename = os.path.join(home, "token.json")
    with open(token_filename, "w") as fh:
        json.dump(token, fh)


def load_jwt():
    token_filename = os.path.join(os.path.expanduser("~"), ".corbett", "token.json")
    if not os.path.exists(token_filename):
        return None
    else:
        with open(token_filename, "r") as fh:
            data = json.load(fh)
            return data["access_token"]


available_apps = [DebuggerApp(), GsheetsApp()]


@click.group
@click.version_option(version)
def cli():
    pass


apps = Group("apps", help="List available and installed apps")


@apps.command(name="list")
def list_apps():
    """
    List available apps to install
    """

    for app in available_apps:
        print(app.name)


@apps.command(name="registered")
def registered_apps():
    """
    List apps installed in your account
    """
    token = load_jwt()
    client = Client(token=token)
    resp = client.send("GET", "/apps")
    if resp.ok:
        print(json.dumps(resp.json()["apps"], indent=2))
    else:
        print(json.dumps(resp.json()))


cli.add_command(apps)


@cli.command()
@option("--email", prompt=True)
@option("--password", prompt=True, confirmation_prompt=True, hide_input=True)
def register(email, password):
    """
    Create a new Corbett account
    """
    client = Client()
    resp = client.register(email, password)
    if not resp.ok:
        raise Exception(str(resp.json()))

    resp = client.login(email=email, password=password)
    if resp.ok:
        save_jwt(resp.json())
        print("Success! You can now install an app with `corbett install gsheets`")
    else:
        raise Exception(str(resp.content))


@cli.command()
@option("--email", prompt=True)
@option("--password", prompt=True, hide_input=True)
def login(email, password):
    """
    Log in to the Corbett API
    """
    client = Client()
    resp = client.login(email=email, password=password)
    if not resp.ok:
        raise Exception(str(resp.content))
    save_jwt(resp.json())
    print("Success! You are now logged in.")


@cli.command()
def whoami():
    """
    Print the currently logged in user's email
    """
    token = load_jwt()
    client = Client(token=token)
    resp = client.whoami()
    data = resp.json()
    if not resp.ok:
        message = f"Error: {data['msg']}\nPlease log in and try again"
        print(message)
    else:
        print(resp.json())


@cli.command()
def debug():
    """
    Check credentials for Snowflake
    """

    config_debug = {
        "api_host": config.api_host,
        "execute_host": config.execute_host,
        "namespace": config.snowflake_namespace,
        "env": config.env,
    }
    print("\nConfig: ")
    for k, v in config_debug.items():
        print(f"  {k}={v}")

    client = Client()
    api_debug = client.healthcheck().json()
    print(
        "\nAPI: ",
    )
    for k, v in api_debug.items():
        if k == "timestamp":
            continue
        print(f"  {k}={v}")

    print("\nSnowflake: ")
    try:
        conn = get_conn()
        cursor = conn.cursor(DictCursor)
        snowflake_debug = cursor.execute(
            "select current_role(), current_user(), current_account()"
        ).fetchall()[0]
        for k, v in snowflake_debug.items():
            print(f"  {k}={v}")
    except Exception as err:
        print(f"   Error: {type(err)} {err}")


@cli.command()
@option(
    "--dry-run",
    is_flag=True,
    flag_value=True,
    help="Print install statements without running them",
)
@option(
    "--verbose",
    "-v",
    is_flag=True,
    flag_value=True,
    help="Print additional details when running installer",
)
@argument("app")
def install(app, dry_run, verbose):
    "Install an app. Use `corbett list-apps` to see available apps"

    token = load_jwt()
    client = Client(token=token)

    for _app in available_apps:
        if _app.name == app:
            target_app = _app
            break
    else:
        print(f"No app named `{app}`")
        exit(1)

    installer = Installer(app=target_app, client=client, verbose=verbose)
    installer.run(dry_run=dry_run)
