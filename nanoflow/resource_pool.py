from __future__ import annotations

import asyncio
import subprocess
from abc import abstractmethod
from collections.abc import Hashable, Sequence

from loguru import logger


class ResourcePool[T: Hashable]:
    def __init__(self, resources: Sequence[T]):
        self.resources = {res: asyncio.Semaphore(1) for res in resources}

    async def acquire(self) -> T:
        while True:
            for res, sem in self.resources.items():
                if sem.locked():
                    continue
                if await sem.acquire():
                    return res
            await asyncio.sleep(0.1)

    def release(self, res: T):
        self.resources[res].release()


class DynamicResourcePool[T](ResourcePool[T]):
    resources: dict[T, asyncio.Semaphore]
    used_resources: set[T]

    def __init__(self):
        self.resources = {}
        self.used_resources = set()

    @abstractmethod
    def get_available_resources(self) -> set[T]: ...

    def update(self):
        available_resources = self.get_available_resources()
        for new_res in available_resources - self.resources.keys():
            logger.info(f"Adding new resource {new_res}")
            self.resources[new_res] = asyncio.Semaphore(1)
        for res in self.resources.keys() - available_resources - self.used_resources:
            logger.info(f"Removing resource {res}")
            self.resources.pop(res)

    async def acquire(self) -> T:
        while True:
            self.update()
            for res, sem in self.resources.items():
                if sem.locked():
                    continue
                if await sem.acquire():
                    self.used_resources.add(res)
                    return res
            await asyncio.sleep(0.1)

    def release(self, res: T):
        self.resources[res].release()
        self.used_resources.remove(res)


class GPUResourcePool(DynamicResourcePool[str]):
    def __init__(self, threshold: float = 0.05):
        self.threshold = threshold
        super().__init__()

    def get_available_resources(self) -> set[str]:
        gpu_info: str = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=memory.used,memory.total", "--format=csv,nounits,noheader"]
        ).decode("utf-8")
        gpus = [tuple(map(int, line.split(","))) for line in gpu_info.strip().split("\n")]

        free_gpus = set()
        for i, (used, total) in enumerate(gpus):
            usage_ratio = used / total
            if usage_ratio <= self.threshold:
                free_gpus.add(str(i))

        return free_gpus


class UnlimitedPool[T](ResourcePool[T]):
    def __init__(self, resource: T):
        self.resource = resource

    async def acquire(self) -> T:
        return self.resource

    def release(self, res: T):
        pass
