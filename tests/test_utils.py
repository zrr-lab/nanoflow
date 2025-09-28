from __future__ import annotations

import os
import subprocess
from unittest.mock import Mock, patch

import pytest

from nanoflow.resource_pool import ResourcePool, UnlimitedPool
from nanoflow.task import Task, TaskProcessError
from nanoflow.utils import create_command, create_gpu_task, create_task, layer_nodes


class TestLayerNodes:
    def test_layer_nodes_simple_dependency(self):
        """Test layering nodes with simple dependencies."""
        dependencies = {"a": [], "b": ["a"], "c": ["b"]}

        layers = layer_nodes(dependencies)

        assert len(layers) == 3
        assert layers[0] == ["a"]
        assert layers[1] == ["b"]
        assert layers[2] == ["c"]

    def test_layer_nodes_parallel_execution(self):
        """Test layering nodes with parallel execution possibilities."""
        dependencies = {"a": [], "b": [], "c": ["a", "b"], "d": ["a"], "e": ["b"]}

        layers = layer_nodes(dependencies)

        assert len(layers) == 2  # The algorithm puts c, d, e all at level 1
        # First layer: independent nodes
        assert set(layers[0]) == {"a", "b"}
        # Second layer: all nodes depending on first layer
        assert set(layers[1]) == {"c", "d", "e"}

    def test_layer_nodes_complex_dependencies(self):
        """Test layering nodes with complex dependency graph."""
        dependencies = {
            "task1": [],
            "task2": [],
            "task3": ["task1"],
            "task4": ["task1", "task2"],
            "task5": ["task3"],
            "task6": ["task4", "task5"],
        }

        layers = layer_nodes(dependencies)

        assert len(layers) == 4
        assert set(layers[0]) == {"task1", "task2"}
        assert set(layers[1]) == {"task3", "task4"}
        assert layers[2] == ["task5"]
        assert layers[3] == ["task6"]

    def test_layer_nodes_single_node(self):
        """Test layering with single node."""
        dependencies = {"single": []}

        layers = layer_nodes(dependencies)

        assert len(layers) == 1
        assert layers[0] == ["single"]

    def test_layer_nodes_empty_dependencies(self):
        """Test layering with empty dependencies."""
        dependencies = {}

        layers = layer_nodes(dependencies)

        assert len(layers) == 0

    def test_layer_nodes_disconnected_components(self):
        """Test layering with disconnected components."""
        dependencies = {"a": [], "b": ["a"], "x": [], "y": ["x"]}

        layers = layer_nodes(dependencies)

        assert len(layers) == 2
        assert set(layers[0]) == {"a", "x"}
        assert set(layers[1]) == {"b", "y"}

    def test_layer_nodes_diamond_dependency(self):
        """Test diamond dependency pattern."""
        dependencies = {"start": [], "left": ["start"], "right": ["start"], "end": ["left", "right"]}

        layers = layer_nodes(dependencies)

        assert len(layers) == 3
        assert layers[0] == ["start"]
        assert set(layers[1]) == {"left", "right"}
        assert layers[2] == ["end"]


class TestCreateCommand:
    @patch("subprocess.Popen")
    def test_create_command_success(self, mock_popen):
        """Test creating and executing a successful command."""
        # Mock successful process
        mock_process = Mock()
        mock_process.wait.return_value = 0
        mock_popen.return_value = mock_process

        command_fn = create_command("test_task", "echo hello")

        # Should not raise any exception
        command_fn()

        mock_popen.assert_called_once_with("echo hello", shell=True, env=None)
        mock_process.wait.assert_called_once()

    @patch("subprocess.Popen")
    def test_create_command_failure(self, mock_popen):
        """Test creating and executing a failing command."""
        # Mock failing process
        mock_process = Mock()
        mock_process.wait.return_value = 1
        mock_popen.return_value = mock_process

        command_fn = create_command("failing_task", "false")

        with pytest.raises(TaskProcessError, match="Task `failing_task` failed with return code 1"):
            command_fn()

    @patch("subprocess.Popen")
    def test_create_command_with_environ(self, mock_popen):
        """Test creating command with custom environment."""
        mock_process = Mock()
        mock_process.wait.return_value = 0
        mock_popen.return_value = mock_process

        custom_env = {"CUSTOM_VAR": "test_value"}
        command_fn = create_command("env_task", "env", environ=custom_env)

        command_fn()

        mock_popen.assert_called_once_with("env", shell=True, env=custom_env)

    @patch("subprocess.Popen")
    def test_create_command_with_update_hook(self, mock_popen):
        """Test creating command with update hook."""
        # Mock process with stdout
        mock_process = Mock()
        mock_process.wait.return_value = 0
        mock_process.stdout = [b"line1\n", b"line2\n"]
        mock_popen.return_value = mock_process

        captured_updates = []

        def update_hook(name: str, line: bytes):
            captured_updates.append((name, line))

        command_fn = create_command("hooked_task", "echo test", update_hook=update_hook)

        command_fn()

        # Should use PIPE for stdout and stderr when update_hook is provided
        mock_popen.assert_called_once_with(
            "echo test", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=None
        )

        assert len(captured_updates) == 2
        assert captured_updates[0] == ("hooked_task", b"line1\n")
        assert captured_updates[1] == ("hooked_task", b"line2\n")

    @patch("subprocess.Popen")
    def test_create_command_with_update_hook_and_environ(self, mock_popen):
        """Test creating command with both update hook and environment."""
        mock_process = Mock()
        mock_process.wait.return_value = 0
        mock_process.stdout = [b"output\n"]
        mock_popen.return_value = mock_process

        custom_env = {"TEST": "value"}

        def update_hook(name: str, line: bytes):
            pass

        command_fn = create_command("test", "cmd", update_hook=update_hook, environ=custom_env)

        command_fn()

        mock_popen.assert_called_once_with(
            "cmd", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=custom_env
        )


class TestCreateGpuTask:
    def test_create_gpu_task_structure(self):
        """Test that create_gpu_task returns a proper Task."""
        pool = ResourcePool([0, 1])

        gpu_task = create_gpu_task("gpu_task", "nvidia-smi", pool=pool)

        assert isinstance(gpu_task, Task)
        assert gpu_task.name == "gpu_task"
        assert gpu_task.resource_pool == pool
        assert gpu_task.resource_modifier is not None

    @patch.dict(os.environ, {}, clear=True)
    def test_create_gpu_task_environment_modification(self):
        """Test that GPU task modifies environment correctly."""
        pool = ResourcePool([0])

        gpu_task = create_gpu_task("gpu_task", "echo $CUDA_VISIBLE_DEVICES", pool=pool)

        # Test the resource modifier
        def dummy_fn():
            return None

        modified_fn = gpu_task.resource_modifier(dummy_fn, 2)  # type: ignore

        # The modifier should return a create_command function
        assert callable(modified_fn)
        if modified_fn is not None:
            modified_fn()

    @patch("nanoflow.utils.create_command")
    def test_create_gpu_task_calls_create_command(self, mock_create_command):
        """Test that create_gpu_task calls create_command with correct environment."""
        pool = ResourcePool([1])

        def mock_update_hook(name: str, line: bytes):
            pass

        mock_create_command.return_value = lambda: None

        gpu_task = create_gpu_task("gpu_test", "nvidia-smi", pool=pool, update_hook=mock_update_hook)

        # Execute the resource modifier
        def dummy_fn():
            return None

        modified_fn = gpu_task.resource_modifier(dummy_fn, 3)  # type: ignore

        # Trigger the modifier to call create_command
        if modified_fn is not None:
            result = modified_fn()
        else:
            result = None

        # Check that create_command was called
        assert mock_create_command.called
        call_args = mock_create_command.call_args

        # Verify the environment contains CUDA_VISIBLE_DEVICES
        environ_arg = call_args[1]["environ"]
        assert "CUDA_VISIBLE_DEVICES" in environ_arg
        assert environ_arg["CUDA_VISIBLE_DEVICES"] == "3"
        assert environ_arg["FORCE_COLOR"] == "1"


class TestCreateTask:
    def test_create_task_without_pool(self):
        """Test creating task without resource pool."""
        task = create_task("test_task", "echo hello")

        assert isinstance(task, Task)
        assert task.name == "test_task"
        assert isinstance(task.resource_pool, UnlimitedPool)
        assert task.resource_modifier is not None

    def test_create_task_with_pool(self):
        """Test creating task with custom resource pool."""
        pool = ResourcePool([1, 2, 3])
        task = create_task("pooled_task", "echo test", pool=pool)

        assert isinstance(task, Task)
        assert task.name == "pooled_task"
        assert task.resource_pool == pool
        assert task.resource_modifier is not None

    def test_create_task_with_update_hook(self):
        """Test creating task with update hook."""

        def update_hook(name: str, line: bytes):
            pass

        task = create_task("hooked_task", "echo test", update_hook=update_hook)

        assert isinstance(task, Task)
        assert task.name == "hooked_task"

    @patch("nanoflow.utils.create_command")
    def test_create_task_calls_create_command(self, mock_create_command):
        """Test that create_task calls create_command with correct environment."""

        def mock_update_hook(name: str, line: bytes):
            pass

        mock_create_command.return_value = lambda: None

        task = create_task("test", "echo hello", update_hook=mock_update_hook)

        # Execute the resource modifier
        def dummy_fn():
            return None

        modified_fn = task.resource_modifier(dummy_fn, "resource")  # type: ignore

        # This should trigger create_command
        if modified_fn is not None:
            result = modified_fn()
        else:
            result = None

        # Check that create_command was called
        assert mock_create_command.called
        call_args = mock_create_command.call_args

        # Verify the environment contains FORCE_COLOR
        environ_arg = call_args[1]["environ"]
        assert "FORCE_COLOR" in environ_arg
        assert environ_arg["FORCE_COLOR"] == "1"

    @patch.dict(os.environ, {"EXISTING_VAR": "existing_value"}, clear=True)
    @patch("nanoflow.utils.create_command")
    def test_create_task_preserves_environment(self, mock_create_command):
        """Test that create_task preserves existing environment variables."""
        mock_create_command.return_value = lambda: None

        task = create_task("env_test", "env")

        # Execute the resource modifier
        def dummy_fn():
            return None

        modified_fn = task.resource_modifier(dummy_fn, "resource")  # type: ignore
        if modified_fn is not None:
            result = modified_fn()
        else:
            result = None

        # Check environment preservation
        call_args = mock_create_command.call_args
        environ_arg = call_args[1]["environ"]

        assert "EXISTING_VAR" in environ_arg
        assert environ_arg["EXISTING_VAR"] == "existing_value"
        assert environ_arg["FORCE_COLOR"] == "1"
