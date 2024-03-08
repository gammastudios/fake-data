import re
from typer.testing import CliRunner

from fake_data.generate_fake_data import app

runner = CliRunner()


def test_fake_data_cli_version():
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert result.stdout == "0.0.1\n"


def test_metadata_ls(monkeypatch, tmp_cache_dir, test_metadata_cache):
    # use the test metadata cache configured via env var
    monkeypatch.setenv("FAKE_DATA_CACHE_DIR", tmp_cache_dir)

    result = runner.invoke(app, ["metadata", "ls"])
    assert result.exit_code == 0
    assert "customer" in result.stdout
    assert "customer_account" in result.stdout


def test_metadata_reset(monkeypatch, tmp_cache_dir, test_metadata_cache):
    # use the test metadata cache configured via env var
    monkeypatch.setenv("FAKE_DATA_CACHE_DIR", tmp_cache_dir)

    result = runner.invoke(app, ["metadata", "reset"])
    assert result.exit_code == 0
    assert re.match(r"^Dropping \d+ existing fake table\(s\).*$", result.stdout)


def test_metadata_refresh(monkeypatch, tmp_cache_dir, test_metadata_cache, customer_csv_file):
    # use the test metadata cache configured via env var

    monkeypatch.setenv("FAKE_DATA_CACHE_DIR", tmp_cache_dir)

    result = runner.invoke(app, ["metadata", "refresh", str(customer_csv_file)])
    assert result.exit_code == 0

    result = runner.invoke(app, ["metadata", "ls"])
    assert result.exit_code == 0
    assert re.match("^.*test_customer$", result.stdout)
