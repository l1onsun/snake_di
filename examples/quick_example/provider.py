from pathlib import Path
from typing import Iterator, TextIO

from examples.quick_example.file_manager import FileManager, Settings
from snake_di import Provider

provider = Provider()


@provider.include_factory
def provide_settings() -> Settings:
    return Settings(file_name="some.txt")


@provider.include_factory(service_type=TextIO)
def provide_file(settings: Settings) -> Iterator[TextIO]:
    Path(settings.file_name).touch()
    with open(settings.file_name, "w") as file:
        yield file
    Path(settings.file_name).unlink()


@provider.include_factory
def provide_file_manager(opened_file: TextIO) -> FileManager:
    return FileManager(opened_file)
