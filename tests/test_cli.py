from typer.testing import CliRunner

from fake_data.generate_fake_data import app

runner = CliRunner()


def test_fake_data_cli_version():
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert result.stdout == "0.0.1\n"
