# Nanoflow
<p align="center">
   <a href="https://python.org/" target="_blank"><img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/nanoflow?logo=python&style=flat-square"></a>
   <a href="https://pypi.org/project/nanoflow/" target="_blank"><img src="https://img.shields.io/pypi/v/nano flow?style=flat-square" alt="pypi"></a>
   <a href="https://pypi.org/project/nanoflow/" target="_blank"><img alt="PyPI - Downloads" src="https://img.shields.io/pypi/dm/nanoflow?style=flat-square"></a>
   <a href="LICENSE"><img alt="LICENSE" src="https://img.shields.io/github/license/nanoflow-dev/nanoflow?style=flat-square"></a>
   <br/>
   <a href="https://github.com/astral-sh/uv"><img alt="uv" src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json&style=flat-square"></a>
   <a href="https://github.com/astral-sh/ruff"><img alt="ruff" src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json&style=flat-square"></a>
   <a href="https://gitmoji.dev"><img alt="Gitmoji" src="https://img.shields.io/badge/gitmoji-%20😜%20😍-FFDD67?style=flat-square"></a>
</p>

Nanoflow is a simple and efficient workflow framework for Python. It allows you to define and execute tasks and workflows with ease.

## Features

- Define tasks and workflows using decorators
- Support for task dependencies
- Retry functionality for tasks
- GPU resource management for parallel task execution

## Roadmap
- [x] Split commands into command and args to avoid too long
- [ ] Integration with FastAPI for managing workflows as web APIs
- [ ] Enhance TUI, improve task log display, use terminal-like style
- [ ] Support for multiple configuration files or folders
- [ ] Support for passing parameters and matrix
- [ ] Support to depend on a task that has matrix

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
