from __future__ import annotations

import functools
import inspect
from contextlib import asynccontextmanager, contextmanager
from dataclasses import dataclass, field
from typing import (
    AsyncContextManager,
    AsyncIterator,
    Callable,
    ContextManager,
    Generic,
    Type,
)

from pure_di._types import Service, TService


@dataclass
class _Inspector(Generic[TService]):
    initial_callable: Callable
    signature: inspect.Signature = field(init=False)

    def __post_init__(self):
        self.signature = inspect.signature(self.initial_callable)

    def get_argument_annotations(self) -> list[Type[Service]]:
        for parameter in self.signature.parameters.values():
            if parameter.annotation is inspect.Signature.empty:
                raise TypeError(
                    f"{self.initial_callable.__name__} parameter {parameter}"
                    f" does not have annotation"
                )
        return [
            parameter.annotation for parameter in self.signature.parameters.values()
        ]

    def get_return_annotation(self) -> Type[TService]:
        # ToDo handle types like ContextManager[T]
        # ToDo: try handle ForwardRef
        if self.signature.return_annotation is inspect.Signature.empty:
            raise TypeError(
                f"{self.initial_callable.__name__} does not have return annotation"
            )
        return self.signature.return_annotation

    def wrap_to_async_context_manager(
        self,
    ) -> Callable[..., AsyncContextManager[TService]]:
        if inspect.iscoroutinefunction(self.initial_callable):

            @asynccontextmanager
            @functools.wraps(self.initial_callable)
            async def _build(*args: Service) -> AsyncIterator[TService]:
                yield await self.initial_callable(*args)

        elif inspect.isasyncgenfunction(self.initial_callable):
            _build = asynccontextmanager(self.initial_callable)

        elif inspect.isgeneratorfunction(self.initial_callable):
            _sync_context_build = contextmanager(self.initial_callable)

            @asynccontextmanager
            @functools.wraps(self.initial_callable)
            async def _build(*args: Service) -> AsyncIterator[TService]:
                with _sync_context_build(*args) as result:
                    yield result

        else:

            @asynccontextmanager
            @functools.wraps(self.initial_callable)
            async def _build(*args: Service) -> AsyncIterator[TService]:
                yield self.initial_callable(*args)

        return _build

    def wrap_to_sync_context_manager(self) -> Callable[..., ContextManager[TService]]:
        if inspect.isgeneratorfunction(self.initial_callable):
            _build = contextmanager(self.initial_callable)
        else:

            @contextmanager
            @functools.wraps(self.initial_callable)
            def _build(*args: Service):
                yield self.initial_callable(*args)

        return _build
