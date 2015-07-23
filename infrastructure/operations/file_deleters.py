import os
from abc import ABCMeta, abstractmethod

from infrastructure.context import helpers

from infrastructure.facilities.mocking import Mockable


class BaseFileDeleter(Mockable):
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, *args, **kwargs):
        pass

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

    @helpers.job_step
    def delete_file(self, filename):
        os.remove(filename)


@BaseFileDeleter.register_default_noop
class NoOpFileDeleter(BaseFileDeleter):
    def __init__(self):
        pass

    @helpers.job_step
    def delete_file(self, filename):
        pass
