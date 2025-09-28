from __future__ import annotations

from typer.testing import CliRunner

from nanoflow.__main__ import app as main_app
from nanoflow.cli import app, init_logger


class TestCLI:
    def test_init_logger(self):
        """Test logger initialization."""

        from rich.logging import RichHandler

        handler = RichHandler()
        init_logger("INFO", handler)

        # This test ensures the function runs without error
        # The actual logger setup is internal to loguru

    def test_try_run_command(self):
        """Test the try_run command."""
        runner = CliRunner()
        result = runner.invoke(app, ["try-run", "./examples/simple.toml"])

        # Should succeed and show the workflow structure
        assert result.exit_code == 0
        assert "echo" in result.output

    def test_run_with_try_run_and_use_tui(self):
        """Test run command with both try_run and use_tui flags."""
        runner = CliRunner()
        result = runner.invoke(app, ["run", "./examples/simple.toml", "--try-run", "--use-tui"])

        # Should succeed and show warning about use-tui being ignored
        assert result.exit_code == 0
        assert "ignored" in result.output or "use-tui" in result.output

    def test_main_app_is_same(self):
        """Test that main app is the same as cli app."""
        assert main_app is app

    def test_run_command_basic_structure(self):
        """Test basic structure of run command without actually executing workflows."""
        # This test verifies the command structure exists
        from nanoflow.cli import run

        # Function should exist and be callable
        assert callable(run)

        # Check function signature has expected parameters
        import inspect

        sig = inspect.signature(run)
        params = list(sig.parameters.keys())

        assert "config_path" in params
        assert "use_tui" in params
        assert "try_run" in params
