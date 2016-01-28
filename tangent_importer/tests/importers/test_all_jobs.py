# -*- coding: utf-8 -*-

import unittest

from pydoc import locate

from tangent_importer import import_jobs
from tangent_importer.infrastructure.discover_jobs import get_importers_names


class TestAllJobs(unittest.TestCase):
    importer_packages = [import_jobs]

    def test_importers_run_without_errors(self):
        names, failures = get_importers_names(packages=self.importer_packages,
                                              testable_only=True)

        failed_names = []
        for name in names:
            importer_class = locate(name)
            try:
                importer_class.test()
            except Exception:
                failed_names.append(name)
        self.assertEquals(0, len(failed_names), "Some jobs failed to test: %s"
                          % ', '.join(failed_names))
