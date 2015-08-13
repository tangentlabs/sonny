from abc import ABCMeta, abstractmethod

from infrastructure.context import helpers

from infrastructure.facilities import everything # noqa

from import_jobs.runner import ImporterRunningMixin


class Importer(ImporterRunningMixin):
    __metaclass__ = ABCMeta

    class JobSettings(object):
        """
        Any facility-specific, per-importer overrides should go here, and will
        be picked up by the `job` wrapper, when you `run`
        """
        test_defaults = {}

    def __init__(self):
        self.name = '%s:%s' % \
            (self.__class__.__module__, self.__class__.__name__)

    @helpers.job
    def run_import(self, job):
        self.job = job
        self.do_run()

    @helpers.test_job
    def test_import(self, job):
        self.job = job
        self.do_run()

    @helpers.step
    @abstractmethod
    def do_run(self):
        """
        The importing function
        """
        pass
