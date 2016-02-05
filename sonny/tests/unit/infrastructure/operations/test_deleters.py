# -*- coding: utf-8 -*-

import os.path
import tempfile

import unittest

from sonny.infrastructure.context import helpers
from sonny.infrastructure.facilities import *  # noqa

from sonny.infrastructure.operations.file_deleters import \
    LocalFileDeleter, NoOpFileDeleter


class TempFilesContextManager(object):
    def __init__(self, file_count=1):
        self.file_count = file_count

    def __enter__(self):
        self.filenames = tuple(tempfile.mkstemp()[1] for _ in xrange(self.file_count))

        return self.filenames

    def __exit__(self, _type, exception, value):
        for filename in self.filenames:
            if os.path.isfile(filename):
                os.remove(filename)


class TestLocalFileDeleter(unittest.TestCase):
    deleter = LocalFileDeleter

    def file_exists(self, filename):
        return os.path.isfile(filename)

    @helpers.job
    def test_deleter_deletes(self, job):
        with TempFilesContextManager() as (filename,):
            self.assertTrue(self.file_exists(filename))
            self.deleter().delete_file(filename)
            self.assertFalse(self.file_exists(filename))

    @helpers.job
    def test_deleter_only_deletes_file_provided(self, job):
        with TempFilesContextManager(file_count=2) as (filename1, filename2):
            self.assertTrue(self.file_exists(filename1))
            self.assertTrue(self.file_exists(filename2))
            self.deleter().delete_file(filename1)
            self.assertFalse(self.file_exists(filename1))
            self.assertTrue(self.file_exists(filename2))


class TestNoOpFileDeleter(unittest.TestCase):
    deleter = NoOpFileDeleter

    def file_exists(self, filename):
        return os.path.isfile(filename)

    @helpers.job
    def test_deleter_doesnt_delete(self, job):
        with TempFilesContextManager() as (filename,):
            self.assertTrue(self.file_exists(filename))
            self.deleter().delete_file(filename)
            self.assertTrue(self.file_exists(filename))

    @helpers.job
    def test_deleter_works_with_bogus_file(self, job):
        filename = "completey bogus filename"
        self.deleter().delete_file(filename)
