from __future__ import annotations

from collections.abc import Generator
from itertools import product
from typing import Any, Literal

from pydantic import BaseModel


class DefaultDict(dict):
    def __missing__(self, key: str):
        return f"{{{key}}}"


def flatten_matrix(matrix: dict[str, list[str]]) -> Generator[dict[str, str], Any, None]:
    matrix_keys, matrix_values = zip(*matrix.items(), strict=True)
    product_matrix = product(*matrix_values)
    for values in product_matrix:
        yield DefaultDict(zip(matrix_keys, values, strict=True))


class TaskConfig(BaseModel):
    """Task config.

    Example:
    >>> config = TaskConfig(command="echo", args=["task1"])
    >>> config.get_command()
    'echo task1'
    >>> config = TaskConfig(command="echo", args=["{task}"])
    >>> config.format({"task": "task1"}).get_command()
    'echo task1'
    >>> config.get_command()
    'echo {task}'
    >>> config.format({"task": "task1"}, inplace=True)
    TaskConfig(command='echo', matrix=None, args=['task1'], deps=[])
    >>> config.get_command()
    'echo task1'
    >>> config = TaskConfig(command="echo", args=["{task}"], matrix={"task": ["task1", "task2"]})
    >>> for name, task in config.wrap_matrix("task:{task}").items():
    ...     print(name, task.get_command())
    task:task1 echo task1
    task:task2 echo task2
    """

    command: str
    matrix: dict[str, list[str]] | None = None
    args: list[str] = []
    deps: list[str] = []

    def get_command(self) -> str:
        assert self.matrix is None, "Matrix is not None, you must run wrap_matrix first"
        return f"{self.command} {' '.join(self.args)}"

    def format(
        self, template_values: dict[str, str], *, format_deps: bool = False, inplace: bool = False
    ) -> TaskConfig:
        if inplace:
            task = self
        else:
            task = self.model_copy(deep=True)

        task.command = task.command.format_map(template_values)
        task.args = [arg.format_map(template_values) for arg in task.args]
        if format_deps:
            task.deps = [dep.format_map(template_values) for dep in task.deps]
        return task

    def wrap_matrix(self, name: str) -> dict[str, TaskConfig]:
        assert self.matrix is not None, "You cannot run wrap_matrix without matrix"
        tasks: dict[str, TaskConfig] = {}
        for i, template_values in enumerate(flatten_matrix(self.matrix)):
            task = self.format(template_values, inplace=False)
            task.matrix = None
            task_name = name.format(**template_values)
            if task_name in tasks:
                task_name = f"{task_name}_{i}"
            tasks[task_name] = task
        return tasks


class WorkflowConfig(BaseModel):
    """
    Workflow config.

    Example:
    >>> config = WorkflowConfig(
    ...     name="test",
    ...     resources="gpus",
    ...     tasks={
    ...         "task1": TaskConfig(command="echo 'task1'"),
    ...         "task2": TaskConfig(command="echo 'task2'", deps=["task1"]),
    ...         "task3": TaskConfig(command="echo 'task3'", deps=["task2"]),
    ...     }
    ... )
    >>> sorted(config.to_nodes().items())
    [('0_task1', []), ('0_task2', ['0_task1']), ('0_task3', ['0_task2'])]
    >>> config = WorkflowConfig(
    ...     name="test",
    ...     matrix={"a": ["1", "2"]},
    ...     tasks={
    ...         "task1": TaskConfig(command="echo 'task{a}'"),
    ...         "task2": TaskConfig(command="echo 'task{a}'", deps=["task1"]),
    ...     }
    ... )
    >>> sorted(config.to_nodes().items())
    [('0_task1', []), ('0_task2', ['0_task1']), ('1_task1', []), ('1_task2', ['1_task1'])]
    """

    name: str
    tasks: dict[str, TaskConfig]
    matrix: dict[str, list[str]] | None = None
    resources: Literal["gpus"] | list[str] | None = None

    def model_post_init(self, __context: Any) -> None:
        if self.matrix is None:
            flattened_matrix = [{}]
        else:
            flattened_matrix = flatten_matrix(self.matrix)

        tasks: dict[str, TaskConfig] = {}
        for i, template_values in enumerate(flattened_matrix):
            for task_name, task_config in self.tasks.items():
                if task_config.matrix is not None:
                    wrapped_tasks = task_config.wrap_matrix(task_name)
                    for wrapped_name, wrapped_task in wrapped_tasks.items():
                        wrapped_task_name = f"{i}_{wrapped_name}"
                        task = wrapped_task.format(template_values, inplace=False)
                        task.deps = [f"{i}_{dep}" for dep in task.deps]
                        tasks[wrapped_task_name] = task
                else:
                    task_name = f"{i}_{task_name}"
                    task = task_config.format(template_values, inplace=False)
                    task.deps = [f"{i}_{dep}" for dep in task.deps]
                    tasks[task_name] = task

        self.tasks = tasks

    def to_nodes(self) -> dict[str, list[str]]:
        nodes: dict[str, list[str]] = {}
        for task_name, task_config in self.tasks.items():
            nodes[task_name] = task_config.deps

        return nodes
