import unittest
from ddt import ddt, data, unpack

from infrastructure import context
from infrastructure.facilities import *  # noqa

from infrastructure.operations.loaders import CsvLoader


@ddt
class TestCsvLoader(unittest.TestCase):
    _loader = CsvLoader

    @data(
        # Empty file
        ("", []),
        # Only headers
        ("a,b", []),
        # Single row
        ("a,b\nc,d", [{'a': 'c', 'b': 'd'}]),
        # Multiple rows
        ("C1,C2\nR1V1,R1V2\nR2V1,R2V2", [{'C1': 'R1V1', 'C2': 'R1V2'}, {'C1': 'R2V1', 'C2': 'R2V2'}]),
        # Loader trims whitespace
        ("       a  \t   ,   b \n c    , \td", [{'a': 'c', 'b': 'd'}]),
    )
    @unpack
    @context.create_for_job
    def test_loader_output(self, contents, expected):
        _file = contents.split('\n')

        results = list(self._loader().get_all_data_with_headers_from_file(_file))
        self.assertEqual(results, expected)
