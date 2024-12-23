from __future__ import annotations

import asyncio
import datetime
from collections.abc import Callable

import humanize
from loguru import logger
from pydantic import BaseModel

from .config import WorkflowConfig
from .resource_pool import GPUResourcePool, ResourcePool
from .task import Task
from .utils import create_gpu_task, create_task, layer_nodes


class ExecutorState(BaseModel):
    total_task_count: int
    running_task_count: int = 0
    completed_task_count: int = 0
    failed_task_count: int = 0

    @property
    def remaining_task_count(self) -> int:
        return self.total_task_count - self.completed_task_count - self.failed_task_count

    @property
    def progress(self) -> str:
        return f"{self.completed_task_count}/{self.total_task_count}"


class Executor:
    def __init__(self, tasks: list[list[Task[..., None]]]):
        self.tasks = tasks
        self.state = ExecutorState(total_task_count=sum(len(layer) for layer in tasks))

    @classmethod
    def from_configs(
        cls,
        config: WorkflowConfig,
        update_hook: Callable[[str, bytes], None] | None = None,
    ) -> Executor:
        logger.info("Creating GPU resource pool and parallel tasks")
        layered_nodes = layer_nodes(config.to_nodes())
        resources = config.resources
        if resources == "gpus":
            resource_pool = GPUResourcePool()
            layered_tasks = [
                [
                    create_gpu_task(node, config.tasks[node].get_command(), pool=resource_pool, update_hook=update_hook)
                    for node in nodes
                ]
                for nodes in layered_nodes
            ]
        else:
            if resources is not None:
                logger.warning("Use of custom resources is experimental and may not work as expected")
                resource_pool = ResourcePool(resources)
            else:
                resource_pool = None
            layered_tasks = [
                [
                    create_task(node, config.tasks[node].get_command(), pool=resource_pool, update_hook=update_hook)
                    for node in nodes
                ]
                for nodes in layered_nodes
            ]

        return cls(layered_tasks)

    async def run_async(self):
        for tasks in self.tasks:
            start_time = asyncio.get_event_loop().time()
            logger.info(f"Starting execution of [blue]{len(tasks)} tasks[/blue]")
            running_tasks = [task.submit() for task in tasks]
            self.state.running_task_count = len(running_tasks)
            while len(running_tasks) > 0:
                await asyncio.sleep(0.1)
                completed_tasks = [task for task in running_tasks if task.done()]
                if not completed_tasks:
                    continue
                running_tasks = [task for task in running_tasks if not task.done()]
                self.state.completed_task_count += len(completed_tasks)
                self.state.running_task_count -= len(running_tasks)
            end_time = asyncio.get_event_loop().time()
            logger.info(
                f"Execution completed [blue]{self.state.progress}[/blue], actual time taken: "
                f"[blue]{humanize.precisedelta(datetime.timedelta(seconds=end_time - start_time))}[/blue]"
            )

    def run(self):
        asyncio.run(self.run_async())
