# Snake DI
![ci](https://github.com/l1onsun/snake_di/actions/workflows/ci.yml/badge.svg)
[![coverage](https://img.shields.io/badge/coverage-100%25-%2334D058)](https://github.com/l1onsun/snake_di/actions/workflows/quality-assurance.yml)
![pypi](https://img.shields.io/pypi/v/snake-di?color=%2334D058)
![python](https://img.shields.io/pypi/pyversions/snake-di.svg?color=%2334D058)

**Source Code**: https://github.com/l1onsun/snake_di  

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

### 1.0.0 Roadmap
- [ ] Documentation
- [ ] Pytest fixtures support
- [ ] Selective builds - allow build only necessary components  
- [ ] More helpful exception messages  
- [ ] Scopes - reuse factories for different app configurations  


### Quick example
`file_manager.py`
```python
@dataclass
class FileManager:
    opened_file: typing.TextIO
    
    def do_some_file_work(self): 
      ...
    
@dataclass
class Settings:
    file_name: str
```
`provider.py`
```python
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
`main.py`
```python
def main():
    with provider.build() as container:
        assert container.keys() == {Settings, TextIO, FileManager}
        file_manager = container[FileManager]
        file_manager.do_some_file_work()

        assert container[TextIO].closed is False
    assert container[TextIO].closed is True
```
Override example - Multiple providers: 
```python
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
Integration with `pytest` example:
```python
from snake_di.pytest import pytest_provide

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
`Container.partial_solve()` example
```python
def handle_data(file_manager: FileManager, settings: Settings, data: str):
  ...

def main():
    with provider.build() as container:
        handle_data_solved = container.partial_solve(handle_data)
        handle_data_solved(data="data")
```
