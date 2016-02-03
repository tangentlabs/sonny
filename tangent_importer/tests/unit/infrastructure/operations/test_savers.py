# -*- coding: utf-8 -*-

import unittest

from tangent_importer.infrastructure.context import helpers
from tangent_importer.infrastructure.facilities import *  # noqa

from tangent_importer.infrastructure.operations.savers import PrintSaver


# TODO: Add test for DbSaver, creating a local DB for testing from config


class TestPrintSaver(unittest.TestCase):
    saver = PrintSaver

    @helpers.job
    def test_print_saver_works(self, job):
        self.saver().save([])
        self.saver().save_no_data()