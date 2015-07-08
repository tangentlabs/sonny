import sys

import utils

from infrastructure import context


class ImporterRunningMixin(object):
    """
    Helper functionality to run an importing job
    """

    @classmethod
    @context.create_for_job
    def run(cls, *args, **kwargs):
        """
        Run the import, creating a job context
        """

        importer = cls(*args, **kwargs)
        importer.run_import()

    @classmethod
    def run_from_command_line(cls, sysargs=None):
        """
        Run the import, taking arguments from the command line
        """

        if sysargs is None:
            sysargs = sys.argv[1:]
        args, kwargs = cls.args_and_kwargs_from_command_line(sysargs)
        cls.run(*args, **kwargs)

    @classmethod
    @context.create_for_job
    @context.method_using_current_job("mock_registry", "logger", "profiler")
    def test(cls, mock_registry, logger, profiler, *args, **kwargs):
        """
        Test the import with auto-mocking, creating a job context
        """

        mock_registry.register_auto_mocks_for_local_testing()

        try:
            importer = cls(*args, **kwargs)
            importer.run_import()
        finally:
            print '*********** LOGS: ***********'
            print logger

            print '*********** PROFILING: ***********'
            print profiler

    @classmethod
    def test_from_command_line(cls, sysargs=None):
        """
        Test the import, taking arguments from the command line
        """

        if sysargs is None:
            sysargs = sys.argv[1:]
        args, kwargs = cls.args_and_kwargs_from_command_line(sysargs)
        cls.test(*args, **kwargs)

    @classmethod
    def args_and_kwargs_from_command_line(cls, sysargs):
        """
        Find out which command line arguments are positional, and which named
        """

        if '--' not in sysargs:
            args = sysargs
            kwargs = {}

            return args, kwargs

        dash_dash_index = sysargs.index('--')
        args, kwargs_list = \
            sysargs[:dash_dash_index], sysargs[dash_dash_index + 1:]

        splitted_kwargs = [kwarg.split('=') for kwarg in kwargs_list]
        kwargs = {
            splitted_kwarg[0]: '='.join(splitted_kwarg[1:])
            for splitted_kwarg in splitted_kwargs
        }

        return args, kwargs


class BaseImporter(ImporterRunningMixin):
    """
    A basic interface for importers
    """

    job_config_filename = None
    """
    Config for specific import. It should be a YAML that contains the config
    for each environment
    """

    @utils.must_be_implemented_by_subclasses
    def run_import(self):
        """
        The main function that does all the importing
        """

        pass

    @property
    @context.method_using_current_job("config")
    def job_environment_config(self, config):
        if not hasattr(self, "_job_environment_config"):
            self._job_environment_config = \
                config.get_job_environment_config(self.job_config_filename)

        return self._job_environment_config
