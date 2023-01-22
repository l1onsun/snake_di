from enum import Enum, auto
from typing import Any, Dict, Type, TypeVar

from typing_extensions import TypeAlias

Service: TypeAlias = Any
ContainerDict = Dict[Type[Service], Service]

TService = TypeVar("TService")


class _Empty(Enum):
    empty = auto()
