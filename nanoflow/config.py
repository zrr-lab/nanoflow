from __future__ import annotations

from itertools import product
from typing import Any, Literal

from pydantic import BaseModel


class TaskConfig(BaseModel):
    """Task config.

    Example:
    >>> config = TaskConfig(command="echo", args=["task1"])
    >>> config.get_command()
    'echo task1'
    >>> config = TaskConfig(command="echo {task}", args=["task1"])
    >>> config.format({"task": "task1"})
    TaskConfig(command='echo task1', args=['task1'], deps=[])
    """

    command: str
    args: list[str] = []
    deps: list[str] = []

    def get_command(self) -> str:
        return f"{self.command} {' '.join(self.args)}"

    def format(self, template_values: dict[str, str], inplace: bool = False) -> TaskConfig:
        if inplace:
            task = self
        else:
            task = self.model_copy(deep=True)

        task.command = task.command.format(**template_values)
        task.args = [arg.format(**template_values) for arg in task.args]
        task.deps = [dep.format(**template_values) for dep in task.deps]
        return task


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

        matrix_keys, matrix_values = zip(*self.matrix.items(), strict=True)
        product_matrix = product(*matrix_values)

        tasks: dict[str, TaskConfig] = {}
        for i, values in enumerate(product_matrix):
            template_values = dict(zip(matrix_keys, values, strict=True))
            for task_name, task_config in self.tasks.items():
                task = task_config.format(template_values)
                task.deps = [f"{i}_{dep}" for dep in task.deps]
                tasks[f"{i}_{task_name}"] = task

        self.tasks = tasks

    def to_nodes(self) -> dict[str, list[str]]:
        nodes: dict[str, list[str]] = {}
        for task_name, task_config in self.tasks.items():
            nodes[task_name] = task_config.deps

        return nodes
