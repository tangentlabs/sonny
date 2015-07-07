# -*- coding: utf-8 -*-

import unittest

from infrastructure import context
from infrastructure.facilities import *  # noqa

from infrastructure.operations.savers import PrintSaver


# TODO: Add test for DbSaver, creating a local DB for testing from config


class TestPrintSaver(unittest.TestCase):
    saver = PrintSaver

    @context.create_for_job
    def test_print_saver_works(self):
        self.saver().save([])
        self.saver().save_no_data()
