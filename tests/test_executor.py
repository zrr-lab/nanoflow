from __future__ import annotations

from unittest.mock import AsyncMock, Mock, patch

import pytest

from nanoflow.config import TaskConfig, WorkflowConfig
from nanoflow.executor import Executor, ExecutorState


class TestExecutorState:
    def test_executor_state_creation(self):
        """Test ExecutorState creation and properties."""
        state = ExecutorState(total_task_count=10)

        assert state.total_task_count == 10
        assert state.running_task_count == 0
        assert state.completed_task_count == 0
        assert state.failed_task_count == 0

    def test_executor_state_remaining_tasks(self):
        """Test remaining task count calculation."""
        state = ExecutorState(total_task_count=10, completed_task_count=3, failed_task_count=2)

        assert state.remaining_task_count == 5  # 10 - 3 - 2

    def test_executor_state_progress(self):
        """Test progress string formatting."""
        state = ExecutorState(total_task_count=10, completed_task_count=6)

        assert state.progress == "6/10"

    def test_executor_state_all_values(self):
        """Test ExecutorState with all values set."""
        state = ExecutorState(total_task_count=20, running_task_count=3, completed_task_count=12, failed_task_count=1)

        assert state.remaining_task_count == 7  # 20 - 12 - 1
        assert state.progress == "12/20"


class TestExecutor:
    def test_executor_creation(self):
        """Test basic Executor creation."""
        layered_tasks = [[Mock(name="task1"), Mock(name="task2")], [Mock(name="task3")]]  # type: ignore

        executor = Executor(layered_tasks)  # type: ignore

        assert executor.tasks == layered_tasks
        assert executor.state.total_task_count == 3
        assert executor.state.completed_task_count == 0
        assert executor.state.failed_task_count == 0

    @pytest.mark.asyncio
    async def test_executor_run_async_basic(self):
        """Test basic async execution."""
        # Create mock tasks
        mock_task1 = Mock()
        mock_task1.submit.return_value = AsyncMock()
        mock_task1.submit.return_value.done.return_value = True

        mock_task2 = Mock()
        mock_task2.submit.return_value = AsyncMock()
        mock_task2.submit.return_value.done.return_value = True

        layered_tasks = [[mock_task1], [mock_task2]]
        executor = Executor(layered_tasks)  # type: ignore

        # Mock asyncio.sleep to speed up test
        with patch("asyncio.sleep", new_callable=AsyncMock):
            await executor.run_async()

        # Verify tasks were submitted
        mock_task1.submit.assert_called_once()
        mock_task2.submit.assert_called_once()

        # Verify state was updated
        assert executor.state.completed_task_count == 2

    def test_executor_run_sync(self):
        """Test synchronous run method."""
        mock_task = Mock()
        mock_task.submit.return_value = AsyncMock()
        mock_task.submit.return_value.done.return_value = True

        layered_tasks = [[mock_task]]
        executor = Executor(layered_tasks)  # type: ignore

        # Mock the async run method
        with patch.object(executor, "run_async", new_callable=AsyncMock) as mock_run_async:
            executor.run()

        mock_run_async.assert_called_once()

    @patch("nanoflow.executor.create_task")
    @patch("nanoflow.executor.layer_nodes")
    def test_from_configs_regular_resources(self, mock_layer_nodes, mock_create_task):
        """Test creating executor from config with regular resources."""
        # Setup mocks - use the actual transformed task names
        mock_layer_nodes.return_value = [["0_task1"], ["0_task2"]]
        mock_create_task.return_value = Mock(name="created_task")

        # Create config
        config = WorkflowConfig(
            name="test",
            tasks={
                "task1": TaskConfig(command="echo", args=["hello"]),
                "task2": TaskConfig(command="echo", args=["world"]),
            },
        )

        executor = Executor.from_configs(config)

        # Verify executor was created
        assert isinstance(executor, Executor)
        assert len(executor.tasks) == 2
        assert len(executor.tasks[0]) == 1  # First layer has 1 task
        assert len(executor.tasks[1]) == 1  # Second layer has 1 task

        # Verify create_task was called for each task
        assert mock_create_task.call_count == 2

    @patch("nanoflow.executor.create_gpu_task")
    @patch("nanoflow.executor.layer_nodes")
    @patch("nanoflow.executor.GPUResourcePool")
    def test_from_configs_gpu_resources(self, mock_gpu_pool, mock_layer_nodes, mock_create_gpu_task):
        """Test creating executor from config with GPU resources."""
        # Setup mocks - use transformed task names
        mock_layer_nodes.return_value = [["0_task1"]]
        mock_create_gpu_task.return_value = Mock(name="gpu_task")
        mock_pool_instance = Mock()
        mock_gpu_pool.return_value = mock_pool_instance

        # Create config with GPU resources
        config = WorkflowConfig(
            name="gpu_test", resources="gpus", tasks={"task1": TaskConfig(command="nvidia-smi", args=[])}
        )

        executor = Executor.from_configs(config)

        # Verify GPU pool was created
        mock_gpu_pool.assert_called_once()

        # Verify create_gpu_task was called
        mock_create_gpu_task.assert_called_once()

        # Verify executor structure
        assert isinstance(executor, Executor)
        assert len(executor.tasks) == 1

    @patch("nanoflow.executor.create_task")
    @patch("nanoflow.executor.layer_nodes")
    @patch("nanoflow.executor.ResourcePool")
    def test_from_configs_custom_resources(self, mock_resource_pool, mock_layer_nodes, mock_create_task):
        """Test creating executor with custom resources."""
        # Setup mocks - use transformed task names
        mock_layer_nodes.return_value = [["0_task1"]]
        mock_create_task.return_value = Mock(name="custom_task")
        mock_pool_instance = Mock()
        mock_resource_pool.return_value = mock_pool_instance

        # Create config with custom resources
        config = WorkflowConfig(
            name="custom_test",
            resources=["device1", "device2"],
            tasks={"task1": TaskConfig(command="echo", args=["test"])},
        )

        with patch("nanoflow.executor.logger") as mock_logger:
            executor = Executor.from_configs(config)

        # Verify warning was logged for experimental feature
        mock_logger.warning.assert_called_once()
        warning_call = mock_logger.warning.call_args[0][0]
        assert "experimental" in warning_call

        # Verify custom resource pool was created
        mock_resource_pool.assert_called_once_with(["device1", "device2"])

    @patch("nanoflow.executor.create_task")
    @patch("nanoflow.executor.layer_nodes")
    def test_from_configs_with_update_hook(self, mock_layer_nodes, mock_create_task):
        """Test creating executor with update hook."""
        mock_layer_nodes.return_value = [["0_task1"]]
        mock_create_task.return_value = Mock()

        config = WorkflowConfig(name="hook_test", tasks={"task1": TaskConfig(command="echo", args=["test"])})

        def update_hook(name: str, data: bytes):
            pass

        executor = Executor.from_configs(config, update_hook=update_hook)

        # Verify create_task was called with update_hook
        call_args = mock_create_task.call_args[1]  # Get keyword arguments
        assert "update_hook" in call_args
        assert call_args["update_hook"] == update_hook

    def test_from_configs_empty_tasks(self):
        """Test creating executor with empty task list."""
        config = WorkflowConfig(name="empty", tasks={})

        executor = Executor.from_configs(config)

        assert isinstance(executor, Executor)
        assert executor.tasks == []
        assert executor.state.total_task_count == 0
