from __future__ import annotations

from contextlib import asynccontextmanager, contextmanager
from dataclasses import dataclass, field
from typing import (
    AsyncIterator,
    Callable,
    Generic,
    Iterator,
    Type,
    TypeVar,
    cast,
    overload,
)

from snake_di._container import Container, _PrivateContainer
from snake_di._factory import _AsyncFactory, _SyncFactory
from snake_di._factory_group import (
    _AsyncFactoryGroup,
    _BaseFactoryGroup,
    _FactoryType,
    _SyncFactoryGroup,
)
from snake_di._types import Service, _Empty
from snake_di.utils import get_generic_first_type

_FactoryGroupType = TypeVar("_FactoryGroupType", bound=_BaseFactoryGroup)


@dataclass
class _BaseProvider(Generic[_FactoryGroupType, _FactoryType]):
    _factories: _FactoryGroupType
    _container: _PrivateContainer = field(default_factory=_PrivateContainer)

    @classmethod
    def from_container(cls, container: _PrivateContainer):
        factory_group_type: Type[_FactoryGroupType] = get_generic_first_type(cls)
        return cls(factory_group_type({}), container)

    @classmethod
    def from_dict(
        cls, service_dict: dict[Type[Service], Service]
    ) -> _BaseProvider:  # Self
        return cls.from_container(_PrivateContainer(service_dict))

    @classmethod
    @overload
    def from_factory(
        cls,
        *,
        service_type: Type[Service] | _Empty = _Empty.empty,
    ) -> Callable[..., _BaseProvider]:  # Self
        ...

    @classmethod
    @overload
    def from_factory(
        cls,
        initial_callable: Callable,
        *,
        service_type: Type[Service] | _Empty = _Empty.empty,
    ) -> _BaseProvider:
        ...

    @classmethod
    def from_factory(
        cls,
        initial_callable: Callable | _Empty = _Empty.empty,
        *,
        service_type: Type[Service] | _Empty = _Empty.empty,
    ):
        def decorator(
            initial_callable_: Callable,
        ) -> _BaseProvider:
            return cls.from_dict({}).include_factory(
                initial_callable_, service_type=service_type
            )

        if initial_callable is _Empty.empty:
            return decorator
        return decorator(initial_callable)

    def _find_factory_to_solve(self) -> tuple[Type[Service], _FactoryType]:
        for service_type, factory in self._factories.items():
            if self._container.check_factory_solvable(factory):
                return service_type, factory
        else:
            raise RuntimeError(
                f"Can not solve any factory {self}"
            )  # ToDo: better errors

    def _clone_with_new_service(
        self, service_type: Type[Service], service: Service
    ) -> _BaseProvider:
        next_factories = self._factories.clone_and_remove(service_type)
        next_container = self._container.clone_and_include(service_type, service)
        # noinspection PyArgumentList
        return type(self)(next_factories, next_container)

    def _merge_self(self, other: _BaseProvider) -> _BaseProvider:
        # noinspection PyArgumentList
        return type(self)(
            _factories=cast(
                _FactoryGroupType, self._factories.merge(other._factories)
            ).remove_keys_from(other._container),
            _container=cast(
                _PrivateContainer, self._container.merge(other._container)
            ).remove_keys_from(other._factories),
        )

    @overload
    def include_factory(
        self, *, service_type: Type[Service] | _Empty = _Empty.empty
    ) -> Callable[[Callable], _BaseProvider]:  # Self
        ...

    @overload
    def include_factory(
        self,
        initial_callable: Callable,
        *,
        service_type: Type[Service] | _Empty = _Empty.empty,
    ) -> _BaseProvider:  # Self
        ...

    def include_factory(
        self,
        initial_callable: Callable | _Empty = _Empty.empty,
        *,
        service_type: Type[Service] | _Empty = _Empty.empty,
    ):
        def decorator(initial_callable_: Callable) -> _BaseProvider:  # Self
            self._factories.include_factory(initial_callable_, service_type)
            self._container.pop(service_type, None)  # type: ignore[arg-type]
            return self

        if initial_callable is _Empty.empty:
            return decorator
        return decorator(initial_callable)

    def _to_async_provider(self) -> AsyncProvider:
        return AsyncProvider(
            _factories=self._factories.to_async_factory_group(),
            _container=self._container,
        )

    def __contains__(self, service_type: Type[Service]) -> bool:
        return service_type in self._factories or service_type in self._container

    def copy(self) -> _BaseProvider:  # Self
        # noinspection PyArgumentList
        return type(self)(self._factories.copy(), self._container.copy())


@dataclass
class AsyncProvider(_BaseProvider[_AsyncFactoryGroup, _AsyncFactory]):
    _factories: _AsyncFactoryGroup = field(default_factory=_AsyncFactoryGroup)

    @asynccontextmanager
    async def build_async(self) -> AsyncIterator[Container]:
        if self._factories.is_empty():
            yield Container(self._container)
            return

        async with self._async_solve_factory() as next_provider:
            async with next_provider.build_async() as result_container:
                yield result_container

    @asynccontextmanager
    async def _async_solve_factory(
        self,
    ) -> AsyncIterator["AsyncProvider"]:
        service_type, factory = self._find_factory_to_solve()
        async with self._container.solve_async_factory(factory) as new_service:
            yield cast(
                AsyncProvider, self._clone_with_new_service(service_type, new_service)
            )

    def _to_async_provider(self) -> AsyncProvider:
        return self

    def __or__(self, other: Provider | AsyncProvider) -> AsyncProvider:
        return cast(AsyncProvider, self._merge_self(other._to_async_provider()))


@dataclass
class Provider(_BaseProvider[_SyncFactoryGroup, _SyncFactory]):
    _factories: _SyncFactoryGroup = field(default_factory=_SyncFactoryGroup)

    @contextmanager
    def build(self) -> Iterator[Container]:
        if self._factories.is_empty():
            yield Container(self._container)
            return

        with self._sync_solve_factory() as next_provider:
            with next_provider.build() as result_container:
                yield result_container

    @contextmanager
    def _sync_solve_factory(self) -> Iterator[Provider]:
        service_type, factory = self._find_factory_to_solve()
        with self._container.solve_sync_factory(factory) as new_service:
            yield cast(
                Provider, self._clone_with_new_service(service_type, new_service)
            )

    @overload
    def __or__(self, other: Provider) -> Provider:
        ...

    @overload
    def __or__(self, other: AsyncProvider) -> AsyncProvider:
        ...

    def __or__(self, other: Provider | AsyncProvider):
        if isinstance(other, Provider):
            return self._merge_self(other)
        return self._to_async_provider()._merge_self(other._to_async_provider())
