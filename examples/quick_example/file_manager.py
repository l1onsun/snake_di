import typing
from dataclasses import dataclass


@dataclass
class FileManager:
    opened_file: typing.TextIO

    def do_some_file_work(self):
        ...


@dataclass
class Settings:
    file_name: str
