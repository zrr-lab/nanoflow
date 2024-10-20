from __future__ import annotations

import asyncio
import os
import subprocess
from collections.abc import Callable

import networkx as nx
from loguru import logger

from .config import WorkflowConfig
from .resource_pool import ResourcePool
from .task import Task, TaskProcessError, task
from .workflow import workflow


@task
def group_parallel_nodes(nodes: dict[str, list[str]]) -> list[list[str]]:
    graph = nx.DiGraph()

    for node, dependencies in nodes.items():
        graph.add_node(node)
        for dependency in dependencies:
            graph.add_edge(dependency, node)

    level = {}
    for node in nx.topological_sort(graph):
        level[node] = max((level[pred] + 1 for pred in graph.predecessors(node)), default=0)

    max_level = max(level.values(), default=-1)
    parallel_nodes = [[] for _ in range(max_level + 1)]
    for node, lvl in level.items():
        parallel_nodes[lvl].append(node)

    return parallel_nodes


@task
def get_available_gpus(threshold=0.05) -> list[str]:
    gpu_info: str = subprocess.check_output(
        ["nvidia-smi", "--query-gpu=memory.used,memory.total", "--format=csv,nounits,noheader"]
    ).decode("utf-8")
    gpus = [tuple(map(int, line.split(","))) for line in gpu_info.strip().split("\n")]

    free_gpus = []
    for i, (used, total) in enumerate(gpus):
        usage_ratio = used / total
        if usage_ratio <= threshold:
            free_gpus.append(str(i))

    return free_gpus


def create_command(
    name: str,
    command: str,
    *,
    update_hook: Callable[[str, bytes], None] | None = None,
    environ: dict[str, str] | None = None,
) -> Callable[[], None]:
    def inner_fn() -> None:
        if update_hook is not None:
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=environ)
            assert process.stdout is not None
            for line in process.stdout:
                update_hook(name, line)
        else:
            process = subprocess.Popen(command, shell=True, env=environ)
        returncode = process.wait()
        if returncode != 0:
            raise TaskProcessError(f"Task `{name}` failed with return code {returncode}")

    return inner_fn


def create_gpu_task(
    name: str,
    command: str,
    *,
    gpu_pool: ResourcePool | None = None,
    update_hook: Callable[[str, bytes], None] | None = None,
) -> Task[[], None]:
    def set_visible_gpu(fn: Callable[[], None], resource: int) -> Callable[[], None]:
        # TODO: To support custom resources, we need to set the resource in the environ
        environ = os.environ.copy()
        environ["CUDA_VISIBLE_DEVICES"] = str(resource)
        environ["FORCE_COLOR"] = "1"
        return create_command(name, command, update_hook=update_hook, environ=environ)

    if gpu_pool is None:
        return task(name=name)(create_command(name, command, update_hook=update_hook))
    else:
        # TODO: support custom_pool
        return task(name=name, resource_pool=gpu_pool, resource_modifier=set_visible_gpu)(lambda: None)


@workflow
async def execute_parallel_tasks(
    config: WorkflowConfig,
    update_hook: Callable[[str, bytes], None] | None = None,
):
    logger.info("Submitting tasks to get available GPUs and group parallel nodes")

    logger.info("Creating GPU resource pool and parallel tasks")
    resources = config.resources
    if resources == "gpus":
        gpu_pool = ResourcePool(get_available_gpus())
    elif resources is not None:
        logger.warning("Use of custom resources is experimental and may not work as expected")
        gpu_pool = ResourcePool(resources)
    else:
        gpu_pool = None

    parallel_tasks = [
        [
            create_gpu_task(node, config.tasks[node].get_command(), gpu_pool=gpu_pool, update_hook=update_hook)
            for node in nodes
        ]
        for nodes in group_parallel_nodes(config.to_nodes())
    ]

    for tasks in parallel_tasks:
        start_time = asyncio.get_event_loop().time()
        logger.info(f"Starting execution of {len(tasks)} tasks")
        await asyncio.gather(*[task.submit() for task in tasks])
        end_time = asyncio.get_event_loop().time()
        logger.info(f"Execution completed, actual time taken: {end_time - start_time:.2f} seconds")
