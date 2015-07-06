import os

import utils
from mockable import Mockable
from logging import log_method_call
from profiling import profile_method


class BaseFileDeleter(Mockable):
    @utils.not_implemented
    def __init__(self, *args, **kwargs):
        pass

    @utils.not_implemented
    def delete_file(self, filename):
        pass

    def delete_files(self, filenames):
        for filename in filenames:
            self.delete_file(filename)


class LocalFileDeleter(BaseFileDeleter):
    def __init__(self):
        pass

    @profile_method
    @log_method_call
    def delete_file(self, filename):
        os.remove(filename)


class NoOpFileDeleter(BaseFileDeleter):
    def __init__(self):
        pass

    @profile_method
    @log_method_call
    def delete_file(self, filename):
        pass
