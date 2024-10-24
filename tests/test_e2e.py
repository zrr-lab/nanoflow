from __future__ import annotations

import pytest


@pytest.mark.benchmark
@pytest.mark.parametrize(
    "config_path",
    ["./examples/simple.toml", "./examples/matrix.toml"],
)
def test_cli(config_path: str):
    from typer.testing import CliRunner

    from nanoflow.__main__ import app

    runner = CliRunner()
    result = runner.invoke(app, ["run", config_path])
    assert result.exit_code == 0, f"Exit code was {result.exit_code}, expected 0. Error: {result.exc_info}"


def test_cli_error():
    from typer.testing import CliRunner

    from nanoflow.__main__ import app

    runner = CliRunner()
    result = runner.invoke(app, ["run", "./examples/error.toml"])
    assert result.exit_code != 0


@pytest.mark.asyncio
async def test_tui():
    import toml

    from nanoflow.config import WorkflowConfig
    from nanoflow.tui import Nanoflow

    workflow_config = WorkflowConfig.model_validate(toml.load("./examples/simple.toml"))
    app = Nanoflow(workflow_config)
    async with app.run_test() as pilot:
        await pilot.press("d")
        await pilot.press("f1")
        assert app.is_running is True
        await pilot.press("q")
        assert app.is_running is False
