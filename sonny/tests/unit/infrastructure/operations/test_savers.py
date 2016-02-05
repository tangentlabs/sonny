# -*- coding: utf-8 -*-

import unittest

from sonny.infrastructure.context import helpers
from sonny.infrastructure.facilities import *  # noqa

from sonny.infrastructure.operations.savers import PrintSaver


# TODO: Add test for DbSaver, creating a local DB for testing from config


class TestPrintSaver(unittest.TestCase):
    saver = PrintSaver

    @helpers.job
    def test_print_saver_works(self, job):
        self.saver().save([])
        self.saver().save_no_data()
