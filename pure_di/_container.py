from __future__ import annotations

import functools
import inspect
from contextlib import asynccontextmanager, contextmanager
from dataclasses import dataclass
from typing import AsyncIterator, Callable, Iterator, Optional, Type

from pure_di._factory import _AsyncFactory, _BaseFactory, _SyncFactory
from pure_di._service_dict import ServiceDict
from pure_di._types import Service, TService


class _PrivateContainer(ServiceDict[Service]):
    @asynccontextmanager
    async def solve_async_factory(
        self, factory: _AsyncFactory[TService]
    ) -> AsyncIterator[TService]:
        deps = [self.data[dep] for dep in factory.dependencies]
        async with factory.async_build(*deps) as service:
            yield service

    @contextmanager
    def solve_sync_factory(self, factory: _SyncFactory[TService]) -> Iterator[TService]:
        deps = [self.data[dep] for dep in factory.dependencies]
        with factory.sync_build(*deps) as service:
            yield service

    def check_factory_solvable(self, factory: _BaseFactory[Service]) -> bool:
        return all([dep in self.data for dep in factory.dependencies])

    def clone_and_include(
        self, service_type: Type[Service], service: Service
    ) -> "_PrivateContainer":
        return self.merge(ServiceDict({service_type: service}))


@dataclass
class Container:
    _private: _PrivateContainer

    def get(self, service_type: Type[TService]) -> Optional[TService]:
        return self._private.get(service_type)

    def keys(self) -> set[Type[Service]]:
        return set(self._private.keys())

    def __getitem__(self, service_type: Type[TService]) -> TService:
        service = self.get(service_type)
        if service is None:
            raise KeyError()  # ToDo: better errors
        return service

    def __repr__(self):
        return f"{type(self).__name__}({repr(self._private)})"

    def partial_solve(self, callable_: Callable) -> Callable:
        sig = inspect.signature(callable_)
        kwargs = {
            p.name: self._private[p.annotation]
            for p in sig.parameters.values()
            if p.annotation in self._private
        }
        return functools.partial(callable_, **kwargs)
