from abc import ABCMeta, abstractmethod, abstractproperty
from datetime import date

from infrastructure.context import helpers

from infrastructure.facilities import everything # noqa

from import_jobs.runner import ImporterRunningMixin


class Importer(ImporterRunningMixin):
    __metaclass__ = ABCMeta

    @abstractproperty
    def uuid(self):
        """
        You need to specify a UUID for each job. The easiest way to do this
        is to get a new value from `uuid.uuid4()` and put that in the class
        """
        pass

    class JobSettings(object):
        """
        Any facility-specific, per-importer overrides should go here, and will
        be picked up by the `job` wrapper, when you `run`
        """
        test_defaults = {}

    def __init__(self, files_to_fetch=None, _today=None):
        self.name = '%s:%s' % \
            (self.__class__.__module__, self.__class__.__name__)

        if isinstance(files_to_fetch, (str, unicode)):
            files_to_fetch = [files_to_fetch]
        self._files_to_fetch = files_to_fetch

        self._today = _today or date.today()

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

    @property
    def files_to_fetch(self):
        if self._files_to_fetch is not None:
            return self._files_to_fetch

        return self.get_files_to_fetch()
