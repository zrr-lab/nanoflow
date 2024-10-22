from __future__ import annotations

import asyncio
from logging import Handler
from pathlib import Path
from typing import Literal

import toml
import typer
from loguru import logger
from rich.highlighter import NullHighlighter
from rich.logging import RichHandler

from nanoflow import WorkflowConfig
from nanoflow.executor import Executor
from nanoflow.utils import layer_nodes

app = typer.Typer()


def init_logger(log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], handler: Handler):
    logger.remove()
    logger.add(handler, format="{message}", level=log_level)


@app.command()
def run(config_path: Path, use_tui: bool = False):
    handler = RichHandler(highlighter=NullHighlighter(), markup=True)
    init_logger("DEBUG", handler)
    workflow_config = WorkflowConfig.model_validate(toml.load(config_path))
    if use_tui:  # pragma: no cover
        from nanoflow.tui import Nanoflow

        app = Nanoflow(workflow_config)
        executor = Executor.from_configs(workflow_config, update_hook=app.update_log)

        async def start():
            await asyncio.gather(executor.workflow(), app.run_async())

        asyncio.run(start())
    else:
        executor = Executor.from_configs(workflow_config)
        executor.run()


@app.command()
def generate_commands(config_path: Path):
    handler = RichHandler(highlighter=NullHighlighter(), markup=True)
    init_logger("DEBUG", handler)
    workflow_config = WorkflowConfig.model_validate(toml.load(config_path))
    layered_nodes = layer_nodes(workflow_config.to_nodes())
    for i, layer in enumerate(layered_nodes):
        logger.info(f"Layer {i}")
        for node in layer:
            print(workflow_config.tasks[node].get_command())
