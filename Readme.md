# Snake DI
![test](https://github.com/lionsoon/snake_di/actions/workflows/nox-test.yml/badge.svg)
![pypi](https://img.shields.io/pypi/v/snake-di?color=%2334D058)
![python](https://img.shields.io/pypi/pyversions/snake-di.svg?color=%2334D058)

**Source Code**: https://github.com/lionsoon/snake_di  
**Features**:
* Lightweight - no external dependencies (only `typing_extensions`)
  * Based on type annotations - no configuration required, less boilerplate
  * Overridable - simple and flexible override system
  * Pytest integration - writing unit tests was never so easy!
  * `yeild` powered - just `yeild` your component and then write closing steps
  * `async` support - able to work with `async` resources

### Install
```commandline
pip install snake-di
```

### Quick examples
```python
# file_manager.py

@dataclass
class FileManager:
    opened_file: typing.TextIO
    
    def do_some_file_work(self): 
      ...
    
@dataclass
class Settings:
    file_name: str
```
```python
# provider.py

from snake_di import Provider

provider = Provider()

@provider.include_factory
def provide_settings() -> Settings:
    return Settings(file_name="some.txt")

@provider.include_factory
def provide_file(settings: Settings) -> TextIO:
    with open(settings.file_name) as file:
        yield file

@provider.include_factory
def provide_file_manager(opened_file: TextIO) -> FileManager:
    return FileManager(opened_file)
```
```python
# main.py

def main():
    with provider.build() as container:
        assert container.keys() == {Settings, TextIO, FileManager}
        file_manager = container[FileManager]
        file_manager.do_some_file_work()

        assert container[TextIO].closed is False
    assert container[TextIO].closed is True
```

```python
# override example

@Provider.from_factory
def change_settings() -> Settings:
    return Settings(file_name="other.txt")

@Provider.from_factory
def mock_file() -> TextIO:
    return unittest.mock.Mock()
    
def main():
    assert type(mock_file) is type(change_settings) is Provider
    assert type(provider | mock_file | change_settings) is Provider
    
    with (provider | mock_file | change_settings).build() as container:
        assert container[Settings].file_name = "other.txt"
        assert type(container[FileManager].opened_file) is unittest.mock.Mock
```

```python
# use with pytest example

@pytest.fixture
def any_usual_fixture():
    return ...

@pytest_provide(provider | mock_file)
def test_with_mocked_file(
    file_manager: FileManager, 
    mocked_file: typing.TextIO, 
    any_usual_fixture
):
    assert type(mocked_file) is unittest.mock.Mock
    assert file_manager.opened_file == mocked_file
```
```python
# container.partial_solve example
def handle_data(file_manager: FileManager, settings: Settings, data: str):
  ...

def main():
    with provider.build() as container:
        handle_data_solved = container.partial_solve(handle_data)
        handle_data_solved(data="data")
```

### Detailed Example 
Let's assume we have following `services.py`, with components we want to build.

```python
# services.py
import ...

@dataclass
class Settings:
    db_uri: str

@dataclass
class Database:
    engine: sqlalchemy.ext.asyncio.AsyncEngine

@dataclass
class Application:
    client: httpx.AsyncClient
    database: Database
    
    async def run(self): ...

```
The main concept of `snake_di` is `Provider` (and `AsyncProvider` if we need async).  
Providers consist of factories - callables that build components. Factories are included to the provider using `provider.include_factory` method/decorator.  
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