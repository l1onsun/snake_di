import pytest

from pure_di import AsyncProvider, Provider


def test_no_return_annotation():
    with pytest.raises(TypeError):

        @Provider.from_factory
        def provide_something():
            return "something"

    with pytest.raises(TypeError):

        @Provider.from_factory
        def provide_something_x(x) -> str:
            return "something" + x


def test_cant_convert_to_factory():
    with pytest.raises(TypeError):
        # noinspection PyTypeChecker
        Provider.from_factory(3)

    with pytest.raises(TypeError):
        # noinspection PyTypeChecker
        AsyncProvider.from_factory(3)
