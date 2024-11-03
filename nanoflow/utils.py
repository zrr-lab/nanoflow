from __future__ import annotations

import os
import subprocess
from collections.abc import Callable

import networkx as nx

from .resource_pool import ResourcePool, UnlimitedPool
from .task import Task, TaskProcessError, task


@task
def layer_nodes(node_dependencies: dict[str, list[str]]) -> list[list[str]]:
    graph = nx.DiGraph()

    for node, dependencies in node_dependencies.items():
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
    pool: ResourcePool,
    update_hook: Callable[[str, bytes], None] | None = None,
) -> Task[[], None]:
    def set_visible_gpu(fn: Callable[[], None], resource: int) -> Callable[[], None]:
        # TODO: To support custom resources, we need to set the resource in the environ
        environ = os.environ.copy()
        environ["CUDA_VISIBLE_DEVICES"] = str(resource)
        environ["FORCE_COLOR"] = "1"
        return create_command(name, command, update_hook=update_hook, environ=environ)

    return task(name=name, resource_pool=pool, resource_modifier=set_visible_gpu)(lambda: None)


def create_task(
    name: str,
    command: str,
    *,
    pool: ResourcePool | None = None,
    update_hook: Callable[[str, bytes], None] | None = None,
) -> Task[[], None]:
    def set_base_environ(fn: Callable[[], None], resource: int) -> Callable[[], None]:
        # TODO: To support custom resources, we need to set the resource in the environ
        environ = os.environ.copy()
        environ["FORCE_COLOR"] = "1"
        return create_command(name, command, update_hook=update_hook, environ=environ)

    if pool is None:
        pool = UnlimitedPool(None)
    return Task(
        name=name,
        fn=lambda: None,
        resource_pool=pool,
        resource_modifier=set_base_environ,
    )
