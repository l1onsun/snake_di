import pytest

SYNC_FIXTURE_VALUE = object()
ASYNC_FIXTURE_VALUE = object()


@pytest.fixture()
def sync_fixture():
    return SYNC_FIXTURE_VALUE


@pytest.fixture()
async def async_fixture():
    return ASYNC_FIXTURE_VALUE
