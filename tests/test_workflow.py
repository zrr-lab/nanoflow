from __future__ import annotations

import asyncio

import pytest

from nanoflow.workflow import Workflow, workflow


class TestWorkflow:
    @pytest.mark.asyncio
    async def test_workflow_creation_and_call(self):
        """Test creating and calling a workflow."""
        result_holder = []

        async def sample_workflow():
            result_holder.append("workflow_result")

        wf = Workflow(name="test_workflow", fn=sample_workflow)
        assert wf.name == "test_workflow"

        await wf()
        assert result_holder == ["workflow_result"]

    @pytest.mark.asyncio
    async def test_workflow_with_parameters(self):
        """Test workflow with parameters."""
        results = []

        async def parameterized_workflow(x: int, y: str = "default"):
            results.append(f"{y}_{x}")

        wf = Workflow(name="param_workflow", fn=parameterized_workflow)

        await wf(42)
        assert results[-1] == "default_42"

        await wf(10, "custom")
        assert results[-1] == "custom_10"

        await wf(5, y="keyword")
        assert results[-1] == "keyword_5"

    def test_workflow_run_sync(self):
        """Test running workflow synchronously."""

        async def simple_workflow() -> None:
            pass

        wf = Workflow(name="sync_workflow", fn=simple_workflow)

        # This should run the async function synchronously
        result = wf.run()
        # Note: run() doesn't return the result, it just executes the workflow
        assert result is None  # run() method returns None

    def test_workflow_run_with_parameters(self):
        """Test running workflow synchronously with parameters."""
        results = []

        async def workflow_with_side_effect(value: str):
            results.append(value)

        wf = Workflow(name="side_effect_workflow", fn=workflow_with_side_effect)
        wf.run("test_value")

        assert results == ["test_value"]


class TestWorkflowDecorator:
    @pytest.mark.asyncio
    async def test_workflow_decorator_simple(self):
        """Test workflow decorator without parameters."""
        results = []

        @workflow
        async def decorated_workflow():
            results.append("decorated_result")

        assert isinstance(decorated_workflow, Workflow)
        assert decorated_workflow.name == "decorated_workflow"

        await decorated_workflow()
        assert results == ["decorated_result"]

    @pytest.mark.asyncio
    async def test_workflow_decorator_with_name(self):
        """Test workflow decorator with custom name."""
        results = []

        @workflow(name="custom_name")
        async def my_workflow():
            results.append("custom_named_result")

        assert isinstance(my_workflow, Workflow)
        assert my_workflow.name == "custom_name"

        await my_workflow()
        assert results == ["custom_named_result"]

    @pytest.mark.asyncio
    async def test_workflow_decorator_with_parameters(self):
        """Test decorated workflow with parameters."""
        results = []

        @workflow(name="param_decorated")
        async def param_workflow(a: int, b: str):
            results.append(f"{b}_{a}")

        await param_workflow(123, "test")
        assert results == ["test_123"]

    def test_workflow_decorator_run_sync(self):
        """Test running decorated workflow synchronously."""
        results = []

        @workflow(name="sync_decorated")
        async def sync_workflow(value: str):
            results.append(f"processed_{value}")

        sync_workflow.run("sync_test")
        assert results == ["processed_sync_test"]

    @pytest.mark.asyncio
    async def test_workflow_decorator_complex_logic(self):
        """Test decorated workflow with complex async logic."""
        results = []

        @workflow
        async def complex_workflow():
            await asyncio.sleep(0.01)  # Simulate async work

            # Simulate some async operations
            async def async_task(n):
                await asyncio.sleep(0.001)
                return n * 2

            tasks = [async_task(i) for i in range(3)]
            task_results = await asyncio.gather(*tasks)

            results.append(sum(task_results))

        await complex_workflow()
        assert results == [6]  # (0*2) + (1*2) + (2*2) = 6

    def test_workflow_decorator_name_inference(self):
        """Test that workflow decorator infers name from function name."""

        @workflow
        async def inferred_name_workflow():
            pass

        assert inferred_name_workflow.name == "inferred_name_workflow"

        @workflow(name=None)  # Explicit None should still infer
        async def another_workflow():
            pass

        assert another_workflow.name == "another_workflow"

    @pytest.mark.asyncio
    async def test_workflow_decorator_error_handling(self):
        """Test error handling in decorated workflows."""

        @workflow
        async def error_workflow():
            raise ValueError("Test error")

        with pytest.raises(ValueError, match="Test error"):
            await error_workflow()

    def test_workflow_decorator_without_parentheses_vs_with(self):
        """Test both forms of the decorator work correctly."""

        # Without parentheses
        @workflow  # type: ignore
        async def workflow1():
            return "result1"

        # With empty parentheses
        @workflow()  # type: ignore
        async def workflow2():
            return "result2"

        # With name parameter
        @workflow(name="custom")  # type: ignore
        async def workflow3():
            return "result3"

        assert isinstance(workflow1, Workflow)
        assert isinstance(workflow2, Workflow)
        assert isinstance(workflow3, Workflow)

        assert workflow1.name == "workflow1"
        assert workflow2.name == "workflow2"
        assert workflow3.name == "custom"
