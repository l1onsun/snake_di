from typing import TextIO

from examples.quick_example.file_manager import FileManager, Settings
from examples.quick_example.provider import provider


def main():
    with provider.build() as container:
        assert container.keys() == {Settings, TextIO, FileManager}
        file_manager = container[FileManager]
        file_manager.do_some_file_work()

        assert container[TextIO].closed is False
    assert container[TextIO].closed is True


if __name__ == "__main__":
    main()
