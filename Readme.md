# Snake DI
![test](https://github.com/lionsoon/snake_di/actions/workflows/nox-test.yml/badge.svg)
![pypi](https://img.shields.io/pypi/v/snake-di?color=%2334D058)
![python](https://img.shields.io/pypi/pyversions/snake-di.svg?color=%2334D058)

**Source Code**: https://github.com/lionsoon/snake_di  
**Features**:
* Lightweight - no external dependencies (only `typing_extensions`)
* Based on type hints - no configuration required, less boilerplate   
* Pytest integration - writing unit tests was never so easy!
* `yeild` powered - just `yeild` your component and then write closing steps
* `async` support - work with `async` resources

### Install
```commandline
pip install snake-di
```
### Example 
Let's assume we have following `services.py` file, witch contains components we want to build.    
For example to be more "real-world" we will use `httpx` and `sqlalchemy` packages:

```python
# services.py
import ...

@dataclass
class Settings:
    db_uri: str

@dataclass
class Database:
    engine: AsyncEngine

@dataclass
class Application:
    client: httpx.AsyncClient
    database: Database
    
    async def run(self): ...

```
The main concept of `snake_di` is `Provider` (and `AsyncProvider` if we need async).  
Providers consist of factories - callables that build components. Factories are included to the provider using `provider.include_factory` method.  
All factory arguments should be annotated. And return type should be specified either by return annotation, or by `service_type` argument (see example below).  

Let's create an `AsyncProvider` for our services in `provider.py` file:

```python
# provider.py
import httpx
from snake_di import AsyncProvider
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine

from services import Settings, Database, Application

provider = AsyncProvider()


@provider.include_factory
def provide_settings() -> Settings:
    return Settings(db_uri="sqlite://...")


@provider.include_factory(service_type=AsyncEngine)
async def provide_engine(settings: Settings):
    engine = create_async_engine(settings.db_uri)
    yield engine
    await engine.dispose()


provider.include_factory(Database, service_type=Database)
provider.include_factory(Application, service_type=Application)
```
Now in `main.py` we can use `provider.build_async` method to construct `Container` in this way:
```python
async with provider.build_async() as container:
    application = container[Application]
```
`Container` is dict-like object that maps service types to service values.
After leaving `async with` context all services in `Container` will be closed (for example `await engine.dispose()` will be run on `AsyncEngine`).  
Container also has `container.partial_solve` method that works similar to `functools.partial` and solves those arguments whose types container contains.  
Full example:
```python
# main.py
from provider import provider
from services import Database, Application

async def do_some_work(database: Database, some_data):
    ...

async def main():
    async with provider.build_async() as container:
        partial_solved_do_some_work = container.partial_solve(do_some_work)
        await partial_solved_do_some_work(some_data="some_data")
        
        await container[Application].run()
```

# Test
Let's write some tests using same example and `pytest`

```python
from snake_di.pytest import pytest_provide_async

from provider import provider
from services import Database
from main import do_some_work


@Provider.from_factory(service_type=Database)
def mock_database():
    return ...


@pytest_provide_async(provider | mock_database)
@pytest.mark.asyncio
async def test_do_some_work(mocked_database: Database, any_usual_fixture):
    await do_some_work(mocked_database, some_data="some_data")
    assert mocked_database.something_to_assert()

```