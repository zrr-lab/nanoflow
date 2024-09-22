from __future__ import annotations

from typer.testing import CliRunner

from nanoflow.__main__ import app

runner = CliRunner()


def test_app():
    result = runner.invoke(app, ["./examples/simple.toml"])
    assert result.exit_code == 0, f"Exit code was {result.exit_code}, expected 0. Error: {result.exc_info}"
