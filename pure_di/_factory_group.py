from __future__ import annotations

from typing import Callable, Type, TypeVar

from typing_extensions import Self

from pure_di._factory import _AsyncFactory, _BaseFactory, _SyncFactory
from pure_di._service_dict import ServiceDict
from pure_di._types import Service, _Empty
from pure_di.utils import get_generic_first_type

_FactoryType = TypeVar("_FactoryType", bound=_BaseFactory)


class _BaseFactoryGroup(ServiceDict[_FactoryType]):
    def clone_and_remove(
        self, service_type: Type[Service]
    ) -> Self:  # type: ignore[valid-type]
        return type(self)(self.copy_data_with_removed(service_type))

    def include_factory(
        self,
        initial_callable: Callable,
        service_type: Type[Service] | _Empty = _Empty.empty,
    ):
        factory_type: Type[_BaseFactory] = get_generic_first_type(self)
        factory = factory_type.from_callable(initial_callable, service_type)
        self.data[factory.service_type] = factory

    def to_async_factory_group(self) -> "_AsyncFactoryGroup":
        return _AsyncFactoryGroup(
            {
                service_type: factory.to_async_factory()
                for service_type, factory in self.items()
            }
        )


class _AsyncFactoryGroup(_BaseFactoryGroup[_AsyncFactory]):
    ...


class _SyncFactoryGroup(_BaseFactoryGroup[_SyncFactory]):
    ...
