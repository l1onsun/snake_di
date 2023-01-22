from __future__ import annotations

from collections import UserDict
from typing import TYPE_CHECKING, Generic, Type, TypeVar

from typing_extensions import Self

from pure_di._types import Service

ServiceDictValue = TypeVar("ServiceDictValue")

if TYPE_CHECKING:
    Base = UserDict[Type[Service], ServiceDictValue]  # pragma: no cover
else:
    Base = UserDict


class ServiceDict(Generic[ServiceDictValue], Base):
    def is_empty(self) -> bool:
        return not self.data

    def merge(
        self, other: ServiceDict[ServiceDictValue]
    ) -> Self:  # type: ignore[valid-type]
        new_data = {}
        new_data.update(self.data)
        new_data.update(other.data)
        # noinspection PyArgumentList
        return type(self)(new_data)

    def remove_keys_from(self, other: ServiceDict) -> Self:  # type: ignore[valid-type]
        for key in other.keys():
            self.pop(key, None)  # type: ignore[arg-type]
        return self

    def copy_data_with_removed(
        self, remove_service_type: Type[Service]
    ) -> dict[Type[Service], ServiceDictValue]:
        new_data = self.data.copy()
        del new_data[remove_service_type]
        return new_data

    def copy(self) -> Self:  # type: ignore[valid-type]
        # noinspection PyArgumentList
        return type(self)(self.data.copy())
