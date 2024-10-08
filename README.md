# Nanoflow

Nanoflow is a simple and efficient workflow framework for Python. It allows you to define and execute tasks and workflows with ease.

## Features

- Define tasks and workflows using decorators
- Support for task dependencies
- Retry functionality for tasks
- GPU resource management for parallel task execution

## Roadmap

- [ ] Integration with FastAPI for managing workflows as web APIs
- [ ] Enhance TUI, improve task log display, use terminal-like style

## Installation [![Downloads](https://pepy.tech/badge/nanoflow)](https://pepy.tech/project/nanoflow)

### Installation using pip/pipx/uv

Before this, please ensure that Python 3.10 or above is installed, along with pip.
```shell
pip install nanoflow
```

If you want to try the Nightly version, you can try
```shell
pip install git+https://github.com/zrr1999/nanoflow@main
```

Before this, please ensure that [pipx](https://github.com/pypa/pipx)/[uv](https://github.com/astral-sh/uv) is installed.
```shell
pipx install nanoflow
uv tool install nanoflow
```

### Source Installation

```shell
git clone https://github.com/zrr1999/nanoflow
cd nanoflow
pip install .
```

## Usage

To use Nanoflow as a package, you can define tasks and workflows using decorators:

```python
from nanoflow import workflow, task

@task
def task_a():
    print("a")

@workflow
async def workflow_a():
    await task_a.submit()


if __name__ == "__main__":
    workflow_a.run()
```

To use Nanoflow as a cli or tui, you can use the following command:

```shell
nanoflow examples/simple.toml
nanoflow examples/simple.toml --use-tui
```
