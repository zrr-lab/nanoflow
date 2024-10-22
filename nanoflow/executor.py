from __future__ import annotations

import asyncio
from collections.abc import Callable

from loguru import logger

from .config import WorkflowConfig
from .resource_pool import ResourcePool
from .utils import create_gpu_task, create_task, get_available_gpus, layer_nodes
from .workflow import Workflow


class Executor:
    def __init__(self, workflow: Workflow):
        # TODO: support multiple workflows
        self.workflow = workflow

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
            gpus = get_available_gpus()
            logger.info(f"Found {len(gpus)} GPUs")
            resource_pool = ResourcePool(gpus)
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

        async def workflow_fn():
            for tasks in layered_tasks:
                start_time = asyncio.get_event_loop().time()
                logger.info(f"Starting execution of {len(tasks)} tasks")
                await asyncio.gather(*[task.submit() for task in tasks])
                end_time = asyncio.get_event_loop().time()
                logger.info(f"Execution completed, actual time taken: {end_time - start_time:.2f} seconds")

        workflow = Workflow(name=config.name, fn=workflow_fn)
        return cls(workflow)

    def run(self):
        self.workflow.run()
