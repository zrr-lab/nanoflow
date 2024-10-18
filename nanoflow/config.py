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
    >>> config = TaskConfig(command="echo", args=["{task}"], matrix={"task": ["task1", "task2"]})
    >>> for task in config.wrap_matrix():
    ...     print(task.get_command())
    echo task1
    echo task2
    """

    command: str
    matrix: dict[str, list[str]] | None = None
    args: list[str] = []
    deps: list[str] = []

    def get_command(self) -> str:
        assert self.matrix is None, "Matrix is not None, you must run wrap_matrix first"
        return f"{self.command} {' '.join(self.args)}"

    def format(self, template_values: dict[str, str], inplace: bool = False) -> TaskConfig:
        if inplace:
            task = self
        else:
            task = self.model_copy(deep=True)

        task.command = task.command.format_map(template_values)
        task.args = [arg.format_map(template_values) for arg in task.args]
        task.deps = [dep.format_map(template_values) for dep in task.deps]
        return task

    def wrap_matrix(self) -> list[TaskConfig]:
        assert self.matrix is not None, "You cannot run wrap_matrix without matrix"
        tasks: list[TaskConfig] = []
        for template_values in flatten_matrix(self.matrix):
            task = self.format(template_values, inplace=False)
            task.matrix = None
            tasks.append(task)
        return tasks


class WorkflowConfig(BaseModel):
    """
    Workflow config.

    Example:
    >>> config = WorkflowConfig(
    >>>     name="test",
    >>>     resources="gpus",
    >>>     tasks={
    >>>         "task1": TaskConfig(command="echo 'task1'"),
    >>>         "task2": TaskConfig(command="echo 'task2'", deps=["task1"]),
    >>>         "task3": TaskConfig(command="echo 'task3'", deps=["task2"]),
    >>>     }
    >>> )
    >>> config.to_nodes()
    {'task1': [], 'task2': ['task1'], 'task3': ['task2']}
    >>> config = WorkflowConfig(
    >>>     name="test",
    >>>     matrix={"a": ["1", "2"]},
    >>>     tasks={
    >>>         "task1": TaskConfig(command="echo 'task{a}'"),
    >>>         "task2": TaskConfig(command="echo 'task{a}'", deps=["task1"]),
    >>>     }
    >>> )
    >>> config.to_nodes()
    {'0_task1': [], '0_task2': ['0_task1'], '1_task1': [], '1_task2': ['1_task1']}
    """

    name: str
    matrix: dict[str, list[str]] | None = None
    tasks: dict[str, TaskConfig]
    resources: Literal["gpus"] | list[str] | None = None

    def model_post_init(self, __context: Any) -> None:
        if self.matrix is None:
            return

        tasks: dict[str, TaskConfig] = {}
        for i, template_values in enumerate(flatten_matrix(self.matrix)):
            for task_name, task_config in self.tasks.items():
                if task_config.matrix is not None:
                    wrapped_tasks = task_config.wrap_matrix()
                    for j, wrapped_task in enumerate(wrapped_tasks):
                        wrapped_task_name = f"{i}_{task_name.format_map(template_values)}_{j}"
                        task = wrapped_task.format(template_values, inplace=False)
                        task.deps = [f"{i}_{dep}" for dep in task.deps]
                        tasks[wrapped_task_name] = task
                else:
                    task_name = f"{i}_{task_name.format_map(template_values)}"
                    task = task_config.format(template_values, inplace=False)
                    task.deps = [f"{i}_{dep}" for dep in task.deps]
                    tasks[task_name] = task

        self.tasks = tasks

    def to_nodes(self) -> dict[str, list[str]]:
        nodes: dict[str, list[str]] = {}
        for task_name, task_config in self.tasks.items():
            nodes[task_name] = task_config.deps

        return nodes
