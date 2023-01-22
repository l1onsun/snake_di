# Pure DI
`Pure DI` is a simple yet powerful dependency injection framework, that will help you connect your components together 
Main features:
* lightweight - no external dependencies (only `typing_extensions`)
* based on type hints - no configuration required, less boilerplate   
* pytest integration - see [#Test](#Test) section, writing unit tests was never so easy!
* `yeild` powered - just `yeild` your component and then write closing steps.
* async support - sometimes we need `await` something in build process.

### Install
```commandline
pip install pure-di
```
### Example 
Let's assume we have following `services.py` file, witch contains components we want to construct.    
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
The main concept in `pure_di` is `Provider` (and `AsyncProvider` if we need async), 
witch contains rules on how to construct components. 
Rules (or factories) are callables, with type annotated arguments. They can be included to the provider using `provider.include_factory` method.
Factory return type should be specified using either by return annotation, either by setting service_type argument. More details about providers see [#Providers](#Providers)  

Let's create an AsyncProvider in `provider.py` file:

```python
# provider.py
import httpx
from pure_di import AsyncProvider
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
Now in `main.py` we can use `provider.build_async` to construct `Container`. 
`Container` is similar to dict, where keys are services types, and values are services. 
It also contains `container.partial_solve` method that works similar to `functools.partial` and solves those arguments whose types it contains.
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
        application = container[Application]
        await application.run()
```

# Test
Let's write some tests using same example and `pytest`

```python
from pure_di.pytest import pytest_provide_async

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