from click.testing import CliRunner
from corbett.cli import cli


def test_cli():
    runner = CliRunner()
    resp = runner.invoke(cli, [])
    assert resp.exit_code == 0
