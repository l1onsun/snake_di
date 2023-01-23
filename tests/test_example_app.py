import pytest

from examples.test_example.factories import async_provider, provider
from examples.test_example.services import (
    AsyncDatabase,
    AsyncDatabaseEngine,
    Database,
    DatabaseEngine,
    Settings,
    UserManager,
)
from snake_di import AsyncProvider, Container, Provider

pytestmark = pytest.mark.anyio


def test_merge_creates_new_provider():
    assert all(
        [
            provider is not provider | async_provider,
            async_provider is not provider | async_provider,
            provider | async_provider is not async_provider | provider,
            provider | async_provider is not provider | async_provider,
        ]
    )


def test_provider_types():
    assert type(provider) is Provider
    assert type(async_provider) is AsyncProvider
    assert type(provider | async_provider) is AsyncProvider

    assert type(Provider.from_dict({})) is Provider
    assert type(provider | Provider.from_dict({})) is Provider


def test_container_repr():
    with Provider().build() as container:
        assert str(container) == "Container({})"


def test_provider_copy():
    copy_provider = provider.copy()
    assert type(copy_provider) is Provider

    @copy_provider.include_factory
    def copy_settings() -> Settings:
        return Settings("copy")

    with copy_provider.build() as container:
        assert container[Database].find() == "copy"

    with provider.build() as container:
        assert container[Database].find() == "db_uri"


def test_example_sync_provider():
    with provider.build() as container:
        assert type(container) is Container
        with pytest.raises(KeyError):
            _ = container[AsyncDatabase]
        assert container.keys() == {
            Settings,
            DatabaseEngine,
            Database,
        }
        assert container[Database].find() == "db_uri"

        def to_be_solved(settings: Settings):
            return settings.db_uri

        assert container.partial_solve(to_be_solved)() == "db_uri"


async def test_example_async_provider():
    async with (provider | async_provider).build_async() as container:
        assert type(container) is Container
        assert container.keys() == {
            Settings,
            DatabaseEngine,
            AsyncDatabaseEngine,
            Database,
            AsyncDatabase,
            UserManager,
        }

        db = container[Database]
        async_db = container[AsyncDatabase]
        assert db.find() == "db_uri"
        assert await async_db.find() == "db_uri"
        assert await container[UserManager].create_user() == "user"

        async def to_be_solved(user_manager: UserManager):
            return await user_manager.create_user()

        assert await container.partial_solve(to_be_solved)() == "user"

    with pytest.raises(RuntimeError):
        db.find()

    with pytest.raises(RuntimeError):
        await async_db.find()


async def test_override_settings():
    with (
        provider | Provider.from_dict({Settings: Settings("other_db_uri")})
    ).build() as container:
        assert container[Database].find() == "other_db_uri"

    async with (
        provider
        | async_provider
        | Provider.from_dict({Settings: Settings("other_db_uri")})
    ).build_async() as container:
        assert await container[AsyncDatabase].find() == "other_db_uri"


def test_provider_from_factory():
    @Provider.from_factory
    def provide_int() -> int:
        return 1

    @Provider.from_factory(service_type=float)
    def provide_float() -> int:
        return 2

    @Provider.from_factory()
    def provide_str(a: int, b: float) -> str:
        return str(a + b)

    provider_ = provide_int | provide_float | provide_str
    assert type(provider_) is Provider
    with (provide_int | provide_float | provide_str).build() as container:
        assert container[str] == "3"


async def test_unsolvable():
    with pytest.raises(RuntimeError):
        async with async_provider.build_async() as _:
            ...
