from click.testing import CliRunner
from corbett.cli import cli
from corbett.version import version


def test_cli():
    runner = CliRunner()
    resp = runner.invoke(cli, [])
    assert resp.exit_code == 0


def test_cli_version():
    runner = CliRunner()
    resp = runner.invoke(cli, ["--version"])
    assert resp.exit_code == 0
    assert version in resp.output
