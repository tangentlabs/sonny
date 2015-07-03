import os

import utils


class BaseFileDeleter(object):
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

    def delete_file(self, filename):
        os.remove(filename)


class NoOpFileDeleter(BaseFileDeleter):
    def __init__(self):
        pass

    def delete_file(self, filename):
        pass
