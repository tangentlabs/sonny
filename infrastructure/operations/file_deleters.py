import os

import utils

from infrastructure import context

from infrastructure.facilities.mocking import Mockable


class BaseFileDeleter(Mockable):
    @utils.must_be_implemented_by_subclasses
    def __init__(self, *args, **kwargs):
        pass

    @utils.must_be_implemented_by_subclasses
    def delete_file(self, filename):
        pass

    def delete_files(self, filenames):
        for filename in filenames:
            self.delete_file(filename)


@BaseFileDeleter.auto_mock_for_local_testing
class LocalFileDeleter(BaseFileDeleter):
    def __init__(self):
        pass

    @context.job_step_method
    def delete_file(self, filename):
        os.remove(filename)


@BaseFileDeleter.register_default_noop
class NoOpFileDeleter(BaseFileDeleter):
    def __init__(self):
        pass

    @context.job_step_method
    def delete_file(self, filename):
        pass