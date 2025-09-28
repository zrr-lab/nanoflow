from __future__ import annotations

import asyncio

import pytest

from nanoflow.resource_pool import ResourcePool, UnlimitedPool
from nanoflow.task import Task, TaskProcessError, task


class TestTask:
    def test_task_creation(self):
        """Test basic task creation."""

        def simple_fn():
            return "result"

        t = Task(name="test_task", fn=simple_fn)
        assert t.name == "test_task"
        assert t.fn == simple_fn
        assert t.retry_interval == [10, 30, 60]
        assert t.resource_pool is None
        assert t.resource_modifier is None

    def test_task_call_sync(self):
        """Test calling task synchronously."""

        def add_numbers(a: int, b: int) -> int:
            return a + b

        t = Task(name="add_task", fn=add_numbers)
        result = t(3, 5)
        assert result == 8

    def test_task_call_with_kwargs(self):
        """Test calling task with keyword arguments."""

        def greet(name: str, greeting: str = "Hello") -> str:
            return f"{greeting}, {name}!"

        t = Task(name="greet_task", fn=greet)

        result1 = t("World")
        assert result1 == "Hello, World!"

        result2 = t("Python", greeting="Hi")
        assert result2 == "Hi, Python!"

    def test_task_with_resource_pool_sync_warning(self, caplog):
        """Test that sync call with resource pool logs a warning."""
        # Intercept loguru logging to caplog
        import logging

        from loguru import logger

        # Create a handler that writes to caplog
        class CaplogHandler(logging.Handler):
            def emit(self, record):
                caplog.records.append(record)

        caplog_handler = CaplogHandler()
        caplog_handler.setLevel(logging.WARNING)

        # Add handler to loguru and remove default
        logger.remove()
        logger.add(caplog_handler, format="{message}", level="WARNING")

        def simple_fn():
            return "result"

        pool = UnlimitedPool("test_resource")
        t = Task(name="test_task", fn=simple_fn, resource_pool=pool)

        result = t()
        assert result == "result"
        # Check that warning was logged
        assert len(caplog.records) > 0
        assert any("resource pool" in record.getMessage() for record in caplog.records)

    def test_task_with_resource_modifier_sync_warning(self, caplog):
        """Test that sync call with resource modifier logs a warning."""
        # Intercept loguru logging to caplog
        import logging

        from loguru import logger

        # Create a handler that writes to caplog
        class CaplogHandler(logging.Handler):
            def emit(self, record):
                caplog.records.append(record)

        caplog_handler = CaplogHandler()
        caplog_handler.setLevel(logging.WARNING)

        # Add handler to loguru and remove default
        logger.remove()
        logger.add(caplog_handler, format="{message}", level="WARNING")

        def simple_fn():
            return "result"

        def modifier(fn, resource):
            return fn

        t = Task(name="test_task", fn=simple_fn, resource_modifier=modifier)

        result = t()
        assert result == "result"
        # Check that warning was logged
        assert len(caplog.records) > 0
        assert any("resource pool or resource modifier" in record.getMessage() for record in caplog.records)

    @pytest.mark.asyncio
    async def test_task_submit_without_resource_pool(self):
        """Test submitting task without resource pool."""

        def compute(x: int) -> int:
            return x * 2

        t = Task(name="compute_task", fn=compute)
        task_future = t.submit(5)

        result = await task_future
        assert result == 10

    @pytest.mark.asyncio
    async def test_task_submit_with_unlimited_pool(self):
        """Test submitting task with unlimited resource pool."""

        def compute(x: int) -> int:
            return x * 3

        pool = UnlimitedPool("unlimited_resource")
        t = Task(name="compute_task", fn=compute, resource_pool=pool)

        task_future = t.submit(4)
        result = await task_future
        assert result == 12

    @pytest.mark.asyncio
    async def test_task_submit_with_resource_pool(self):
        """Test submitting task with regular resource pool."""

        def compute(x: int) -> int:
            return x + 10

        pool = ResourcePool([1, 2])
        t = Task(name="compute_task", fn=compute, resource_pool=pool)

        task_future = t.submit(5)
        result = await task_future
        assert result == 15

    @pytest.mark.asyncio
    async def test_task_submit_with_resource_modifier(self):
        """Test submitting task with resource modifier."""
        results = []

        def base_fn(x: int) -> int:
            results.append(f"base_{x}")
            return x

        def modifier(fn, resource):
            def modified_fn(*args, **kwargs):
                results.append(f"using_resource_{resource}")
                return fn(*args, **kwargs)

            return modified_fn

        pool = UnlimitedPool("test_resource")
        t = Task(name="modified_task", fn=base_fn, resource_pool=pool, resource_modifier=modifier)

        task_future = t.submit(42)
        result = await task_future

        assert result == 42
        assert "using_resource_test_resource" in results
        assert "base_42" in results

    @pytest.mark.asyncio
    async def test_task_submit_multiple_concurrent(self):
        """Test submitting multiple tasks concurrently."""

        def compute(x: int) -> int:
            return x**2

        t = Task(name="square_task", fn=compute)

        # Submit multiple tasks concurrently
        tasks = [t.submit(i) for i in range(5)]
        results = await asyncio.gather(*tasks)

        expected = [i**2 for i in range(5)]
        assert results == expected

    @pytest.mark.asyncio
    async def test_task_submit_with_limited_resource_pool(self):
        """Test task submission with limited resources."""
        execution_order = []

        def tracked_compute(x: int) -> int:
            execution_order.append(f"start_{x}")
            # Simulate some work
            execution_order.append(f"end_{x}")
            return x * 2

        # Pool with only one resource
        pool = ResourcePool([1])
        t = Task(name="tracked_task", fn=tracked_compute, resource_pool=pool)

        # Submit two tasks - they should run sequentially due to resource limit
        tasks = [t.submit(1), t.submit(2)]
        results = await asyncio.gather(*tasks)

        assert results == [2, 4]
        assert len(execution_order) == 4
        assert "start_1" in execution_order
        assert "end_1" in execution_order
        assert "start_2" in execution_order
        assert "end_2" in execution_order


class TestTaskDecorator:
    def test_task_decorator_simple(self):
        """Test task decorator without parameters."""

        @task
        def decorated_task():
            return "decorated_result"

        assert isinstance(decorated_task, Task)
        assert decorated_task.name == "decorated_task"

        result = decorated_task()
        assert result == "decorated_result"

    def test_task_decorator_with_name(self):
        """Test task decorator with custom name."""

        @task(name="custom_task_name")
        def my_task():
            return "custom_result"

        assert isinstance(my_task, Task)
        assert my_task.name == "custom_task_name"

        result = my_task()
        assert result == "custom_result"

    def test_task_decorator_with_resource_pool(self):
        """Test task decorator with resource pool."""
        pool = UnlimitedPool("test_resource")

        @task(resource_pool=pool)
        def pooled_task():
            return "pooled_result"

        assert isinstance(pooled_task, Task)
        assert pooled_task.resource_pool == pool

        result = pooled_task()
        assert result == "pooled_result"

    def test_task_decorator_with_resource_modifier(self):
        """Test task decorator with resource modifier."""

        def modifier(fn, resource):
            def modified(*args, **kwargs):
                return f"modified_{fn(*args, **kwargs)}"

            return modified

        pool = UnlimitedPool("test")

        @task(resource_pool=pool, resource_modifier=modifier)
        def modified_task():
            return "base"

        assert isinstance(modified_task, Task)
        assert modified_task.resource_modifier == modifier

    def test_task_decorator_with_all_parameters(self):
        """Test task decorator with all parameters."""
        pool = UnlimitedPool("resource")

        def modifier(fn, resource):
            return fn

        @task(name="full_task", resource_pool=pool, resource_modifier=modifier)
        def full_task(x: int) -> int:
            return x * 10

        assert isinstance(full_task, Task)
        assert full_task.name == "full_task"
        assert full_task.resource_pool == pool
        assert full_task.resource_modifier == modifier

        result = full_task(5)
        assert result == 50

    @pytest.mark.asyncio
    async def test_decorated_task_submit(self):
        """Test submitting decorated task."""

        @task(name="async_decorated")
        def async_task(x: int) -> int:
            return x + 100

        future = async_task.submit(42)
        result = await future
        assert result == 142

    def test_task_decorator_name_inference(self):
        """Test that task decorator infers name from function name."""

        @task
        def inferred_name_task():
            return "inferred"

        assert inferred_name_task.name == "inferred_name_task"

        @task(name=None)  # Explicit None should still infer
        def another_task():
            return "another"

        assert another_task.name == "another_task"

    def test_task_decorator_without_parentheses_vs_with(self):
        """Test both forms of the decorator work correctly."""

        # Without parentheses
        @task
        def task1():
            return "result1"

        # With empty parentheses
        @task()
        def task2():
            return "result2"

        # With name parameter
        @task(name="custom")
        def task3():
            return "result3"

        assert isinstance(task1, Task)
        assert isinstance(task2, Task)
        assert isinstance(task3, Task)

        assert task1.name == "task1"
        assert task2.name == "task2"
        assert task3.name == "custom"


class TestTaskProcessError:
    def test_task_process_error_creation(self):
        """Test TaskProcessError exception."""
        error = TaskProcessError("Test error message")
        assert str(error) == "Test error message"
        assert isinstance(error, Exception)

    def test_task_process_error_inheritance(self):
        """Test TaskProcessError inheritance."""
        error = TaskProcessError("Test")
        assert isinstance(error, Exception)

        try:
            raise error
        except TaskProcessError as e:
            assert str(e) == "Test"
        except Exception:
            pytest.fail("Should have caught TaskProcessError specifically")
