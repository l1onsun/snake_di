from contextlib import asynccontextmanager, contextmanager
from dataclasses import dataclass
from typing import AsyncIterator, Iterator


@dataclass
class Settings:
    db_uri: str


@dataclass
class DatabaseEngine:
    db_uri: str
    is_opened: bool = False

    @classmethod
    @contextmanager
    def open(cls, db_uri: str) -> Iterator["DatabaseEngine"]:
        engine = cls(db_uri)
        engine.is_opened = True
        yield engine
        engine.is_opened = False

    def find(self):
        if self.is_opened:
            return self.db_uri
        raise RuntimeError("closed")


@dataclass
class AsyncDatabaseEngine:
    db_uri: str
    is_opened: bool = False

    @classmethod
    @asynccontextmanager
    async def open(cls, db_uri: str) -> AsyncIterator["AsyncDatabaseEngine"]:
        engine = cls(db_uri)
        engine.is_opened = True
        yield engine
        engine.is_opened = False

    async def find(self):
        if self.is_opened:
            return self.db_uri
        raise RuntimeError("closed")


@dataclass
class Database:
    engine: DatabaseEngine

    def find(self):
        return self.engine.find()


@dataclass
class AsyncDatabase:
    engine: AsyncDatabaseEngine

    async def find(self):
        return await self.engine.find()


@dataclass
class UserManager:
    sync_db: Database
    async_db: AsyncDatabase

    async def create_user(self):
        assert type(self.sync_db) is Database
        assert type(self.async_db) is AsyncDatabase
        return "user"
