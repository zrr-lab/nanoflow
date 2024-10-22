from __future__ import annotations

import asyncio
from collections.abc import Callable
from typing import Any, Generic, ParamSpec, TypeVar, overload

from loguru import logger
from pydantic import BaseModel, ConfigDict

from .resource_pool import ResourcePool

InputT = ParamSpec("InputT")
RetT = TypeVar("RetT")


class TaskProcessError(Exception):
    """Exception raised when a task process fails."""


class Task(BaseModel, Generic[InputT, RetT]):
    """
    Task to be executed by the workflow.

    Example:
    >>> my_task = Task(name="my_task", fn=lambda: print("Hello, world!"))
    >>> my_task()
    Hello, world!
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)
    name: str
    fn: Callable[InputT, RetT]
    retry_interval: list[int] = [10, 30, 60]
    resource_pool: ResourcePool[Any] | None = None
    resource_modifier: Callable[[Callable[InputT, RetT], Any], Callable[InputT, RetT]] | None = None

    def __call__(self, *args: InputT.args, **kwargs: InputT.kwargs) -> RetT:
        if self.resource_pool is not None or self.resource_modifier is not None:
            logger.warning(
                f"Task `{self.name}` has a resource pool or resource modifier, which is not supported in sync mode"
            )
        return self.fn(*args, **kwargs)

    def submit(self, *args: InputT.args, **kwargs: InputT.kwargs) -> asyncio.Task[RetT]:
        retry_interval = self.retry_interval[:]

        async def wrapper_fn() -> RetT:
            try:
                if self.resource_pool is not None:
                    resource = await self.resource_pool.acquire()
                    logger.info(f"Acquired resource by task [blue]{self.name}[/blue]: {resource}")
                    if self.resource_modifier is not None:
                        fn = self.resource_modifier(self.fn, resource)
                    else:
                        fn = self.fn
                    try:
                        return await asyncio.to_thread(fn, *args, **kwargs)
                    finally:
                        self.resource_pool.release(resource)
                        logger.info(f"Released resource: {resource}")
                else:
                    return await asyncio.to_thread(self.fn, *args, **kwargs)
            except TaskProcessError as e:
                logger.error(f"Failed to execute task: {e}")
                if retry_interval:
                    retry = retry_interval.pop(0)
                    logger.info(f"Retry task `{self.name}` after {retry} seconds")
                    await asyncio.sleep(retry)
                    return await wrapper_fn()
                raise e

        return asyncio.create_task(wrapper_fn())


@overload
def task(fn: Callable[InputT, RetT]) -> Task[InputT, RetT]: ...


@overload
def task(
    *,
    name: str | None = None,
    resource_pool: ResourcePool[Any] | None = ...,
    resource_modifier: Callable[[Callable[InputT, RetT], Any], Callable[InputT, RetT]] | None = None,
) -> Callable[[Callable[InputT, RetT]], Task[InputT, RetT]]: ...


def task(
    fn: Callable[InputT, RetT] | None = None,
    *,
    name: str | None = None,
    resource_pool: ResourcePool[Any] | None = None,
    resource_modifier: Callable[[Callable[InputT, RetT], Any], Callable[InputT, RetT]] | None = None,
) -> Callable[[Callable[InputT, RetT]], Task[InputT, RetT]] | Task[InputT, RetT]:
    """Decorator to create a task.

    Example:
    >>> @task
    >>> def my_task(a: int, b: int) -> int:
    >>>     return a + b
    >>> my_task.name
    'my_task'
    >>> @task(name="custom_name")
    >>> def my_task(a: int, b: int) -> int:
    >>>     return a + b
    >>> my_task.name
    'custom_name'
    """

    def decorator(fn: Callable[InputT, RetT]) -> Task[InputT, RetT]:
        return Task(
            name=name or getattr(fn, "__name__", "unnamed"),
            fn=fn,
            resource_pool=resource_pool,
            resource_modifier=resource_modifier,
        )

    if fn is None:
        return decorator
    return decorator(fn)
