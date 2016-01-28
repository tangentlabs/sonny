# -*- coding: utf-8 -*-

import unittest
from ddt import ddt, data, unpack

from tangent_importer.infrastructure.context import helpers
from tangent_importer.infrastructure.facilities import *  # noqa

from tangent_importer.infrastructure.operations.fetchers import NoOpFetcher


@ddt
class TestNoOpFetcher(unittest.TestCase):
    fetcher = NoOpFetcher

    @data(
        (None,),
        ("filename.csv",),
        (u"Unicodeγιούνικοουντ",),
        (u"nonsensical$<>??<!£~@:}{£$%}\z/,.x'#;][p]+_+_)()_*(&*%&^*$%^&£$%!¬",),
    )
    @unpack
    @helpers.job
    def test_noop_fetcher_returns_filename_passed(self, filename, job):
        result = self.fetcher().fetch_file(filename)

        self.assertEquals(result, filename)
