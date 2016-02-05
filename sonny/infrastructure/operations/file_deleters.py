import os
from abc import abstractmethod

from sonny.infrastructure.context import helpers

from sonny.infrastructure.operations.base import BaseOperation


class BaseFileDeleter(BaseOperation):
    @abstractmethod
    def delete_file(self, filename):
        pass

    def delete_files(self, filenames):
        for filename in filenames:
            self.delete_file(filename)


@BaseFileDeleter.auto_mock_for_local_testing
class LocalFileDeleter(BaseFileDeleter):
    def __init__(self):
        pass

    @helpers.step
    def delete_file(self, filename):
        os.remove(filename)


@BaseFileDeleter.register_default_noop
class NoOpFileDeleter(BaseFileDeleter):
    def __init__(self):
        pass

    @helpers.step
    def delete_file(self, filename):
        pass
