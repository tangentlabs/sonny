import sys

import utils

from infrastructure import context


class ImporterRunningMixin(object):
    """
    Helper functionality to run an importing job
    """

    test_defaults = {}
    """
    Default test arguments
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
        kwargs = cls.kwargs_from_command_line(sysargs)
        cls.run(**kwargs)

    @classmethod
    def test(cls, *args, **kwargs):
        """
        Test the import with auto-mocking, creating a job context
        """

        def register_auto_mocks_for_local_testing(job):
            job.mock_registry.register_auto_mocks_for_local_testing()

        def print_metrics(job):
            print '*********** LOGS: ***********'
            print job.logger

            print '*********** PROFILING: ***********'
            print job.profiler

            print '*********** NOTIFICATIONS: ***********'
            print job.notifier

        test_kwargs = dict(cls.test_defaults)
        test_kwargs.update(kwargs)

        cls.run \
            .bind(cls) \
            .with_before(register_auto_mocks_for_local_testing) \
            .with_finally(print_metrics) \
            .call(**test_kwargs)

    @classmethod
    def test_from_command_line(cls, sysargs=None):
        """
        Test the import, taking arguments from the command line
        """

        if sysargs is None:
            sysargs = sys.argv[1:]
        kwargs = cls.kwargs_from_command_line(sysargs)
        cls.test(**kwargs)

    @classmethod
    def kwargs_from_command_line(cls, sysargs):
        """
        Decompose kwargs from command line
        """

        splitted_kwargs = [kwarg.split('=') for kwarg in sysargs]
        kwargs = {
            splitted_kwarg[0]: '='.join(splitted_kwarg[1:])
            for splitted_kwarg in splitted_kwargs
        }

        return kwargs


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
