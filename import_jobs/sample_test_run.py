import utils

from infrastructure import context
from infrastructure.facilities import logging, profiling  # noqa

from infrastructure.operations.fetchers import FtpFetcher
from infrastructure.operations.savers import DbSaver
from infrastructure.operations.file_deleters import LocalFileDeleter

from import_jobs.sample import SampleImporter

location = utils.make_location(__file__)


@context.create_for_job
@context.function_using_current_job("mock_registry", "logger", "profiler")
def test_main(mock_registry, logger, profiler):
    mock_registry.register_mocks_using_default_noops(
        FtpFetcher,
        LocalFileDeleter,
        DbSaver,
    )

    class MockedImporter(SampleImporter):
        @context.job_step_method
        def ftp_files_to_fetch(self):
            return [location('sample.csv')]

    importer = MockedImporter()
    importer.run_import()

    print '*********** LOGS: ***********'
    print '\n'.join("[%s] %s" % x for x in logger._logs)

    print '*********** PROFILING: ***********'
    print stringify_profiling(profiler.profiling_section)


def stringify_profiling(profiling_section, indent=""):
    return ''.join(
        "\n%s[%s] %s: %.3f%s" % (indent, x.job_step.full_name, x.name, x.duration or -1, stringify_profiling(x, indent="  " + indent))
        for x in profiling_section.profiling_sections
    )


if __name__ == '__main__':
    test_main()
