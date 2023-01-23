from typing import AsyncIterator, Iterator

from example.services import (
    AsyncDatabase,
    AsyncDatabaseEngine,
    Database,
    DatabaseEngine,
    Settings,
    UserManager,
)
from snake_di import AsyncProvider, Provider

provider = Provider()


@provider.include_factory
def provide_settings() -> Settings:
    return Settings("db_uri")


@provider.include_factory(service_type=DatabaseEngine)
def provide_engine(settings: Settings) -> Iterator[DatabaseEngine]:
    with DatabaseEngine.open(settings.db_uri) as engine:
        yield engine


provider.include_factory(Database, service_type=Database)

async_provider = AsyncProvider()


@async_provider.include_factory(service_type=AsyncDatabaseEngine)
async def provide_async_engine(
    settings: Settings,
) -> AsyncIterator[AsyncDatabaseEngine]:
    async with AsyncDatabaseEngine.open(settings.db_uri) as engine:
        yield engine


async_provider.include_factory(AsyncDatabase, service_type=AsyncDatabase)


@async_provider.include_factory
async def provide_user_manager(
    sync_db: Database, async_db: AsyncDatabase
) -> UserManager:
    await async_db.find()
    return UserManager(sync_db, async_db)
