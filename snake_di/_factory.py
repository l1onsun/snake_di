from __future__ import annotations

from dataclasses import dataclass, field
from typing import AsyncContextManager, Callable, ContextManager, Generic, Type

from snake_di._inspector import _Inspector
from snake_di._types import Service, TService, _Empty


@dataclass
class _BaseFactory(Generic[TService]):
    initial_callable: Callable = field(repr=False)
    service_type: Type[TService]
    dependencies: list[Type[Service]]
    _inspector: _Inspector = field(repr=False)

    @classmethod
    def from_callable(
        cls,
        initial_callable: Callable,
        service_type: Type[TService] | _Empty = _Empty.empty,
    ):
        inspector: _Inspector = _Inspector(initial_callable)
        guess_service_type: Type[TService] = (
            service_type
            if service_type is not _Empty.empty
            else inspector.get_return_annotation()
        )
        return cls(
            initial_callable=initial_callable,
            dependencies=inspector.get_argument_annotations(),
            service_type=guess_service_type,
            _inspector=inspector,
        )

    def to_async_factory(self) -> "_AsyncFactory":
        return _AsyncFactory(
            initial_callable=self.initial_callable,
            dependencies=self.dependencies,
            service_type=self.service_type,
            _inspector=self._inspector,
        )


@dataclass
class _AsyncFactory(_BaseFactory[TService]):
    async_build: Callable[..., AsyncContextManager[TService]] = field(init=False)

    def __post_init__(self):
        self.async_build = self._inspector.wrap_to_async_context_manager()


@dataclass
class _SyncFactory(_BaseFactory[TService]):
    sync_build: Callable[..., ContextManager[TService]] = field(init=False)

    def __post_init__(self):
        self.sync_build = self._inspector.wrap_to_sync_context_manager()
