import functools
import inspect
from typing import Callable

from snake_di import AsyncProvider, Provider
from snake_di._provider import _BaseProvider


def pytest_provide(provider: Provider):
    def decorate(initial_test: Callable):
        @functools.wraps(initial_test)
        def new_test_func(*args, **kwargs):
            with provider.build() as container:
                return container.partial_solve(initial_test)(*args, **kwargs)

        new_test_func.__signature__ = _fix_signature(  # type: ignore[attr-defined]
            provider, initial_test
        )
        _inherit_pytest_mark(new_test_func, initial_test)
        return new_test_func

    return decorate


def pytest_provide_async(provider: AsyncProvider):
    def decorate(initial_test: Callable):
        @functools.wraps(initial_test)
        async def new_test_func(*args, **kwargs):
            async with provider.build_async() as container:
                return await container.partial_solve(initial_test)(*args, **kwargs)

        new_test_func.__signature__ = _fix_signature(  # type: ignore[attr-defined]
            provider, initial_test
        )
        _inherit_pytest_mark(new_test_func, initial_test)
        return new_test_func

    return decorate


def _fix_signature(provider: _BaseProvider, initial_test: Callable):
    initial_sig = inspect.signature(initial_test)
    parameters = list(initial_sig.parameters.values())
    new_parameters = [param for param in parameters if param.annotation not in provider]
    return initial_sig.replace(parameters=new_parameters)


def _inherit_pytest_mark(new_test_func: Callable, initial_test_func):
    pytestmark = getattr(initial_test_func, "pytestmark", None)
    if pytestmark is not None:
        new_test_func.pytestmark = pytestmark  # type: ignore[attr-defined]
