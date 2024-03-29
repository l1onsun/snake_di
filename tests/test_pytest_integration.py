import pytest

from snake_di.pytest import pytest_provide, pytest_provide_async
from tests.app.factories import async_provider, provider
from tests.app.services import Settings, UserManager
from tests.conftest import ASYNC_FIXTURE_VALUE, SYNC_FIXTURE_VALUE


@pytest_provide(provider)
def test_provide_by_type(settings: Settings, sync_fixture):
    assert settings.db_uri == "db_uri"
    assert sync_fixture == SYNC_FIXTURE_VALUE


@pytest_provide_async(provider | async_provider)
@pytest.mark.anyio
async def test_provide_by_type_async(user_manager: UserManager, async_fixture):
    assert await user_manager.create_user() == "user"
    assert async_fixture == ASYNC_FIXTURE_VALUE


@pytest.mark.anyio
async def test_mark():
    assert test_provide_by_type_async.pytestmark == test_mark.pytestmark
