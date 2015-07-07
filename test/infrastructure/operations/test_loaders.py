import unittest

from infrastructure import context
from infrastructure.facilities import *  # noqa

from infrastructure.operations.loaders import CsvLoader


class TestCsvLoader(unittest.TestCase):
    @context.create_for_job
    def test_empty_file(self):
        contents = ""
        _file = contents.split('\n')

        results = list(CsvLoader().get_all_data_with_headers_from_file(_file))
        self.assertEqual(results, [])
