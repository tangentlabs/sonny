from abc import ABCMeta, abstractmethod

from infrastructure import context

from import_jobs.runner import ImporterRunningMixin


class BaseImporter(context.get_helpers_mixin(), ImporterRunningMixin):
    __metaclass__ = ABCMeta

    """
    A basic interface for importers
    """

    job_config_filename = None
    """
    Config for specific import. It should be a YAML that contains the config
    for each environment
    """

    @context.register_current_job_importer
    def __new__(cls, *args, **kwargs):
        return super(BaseImporter, cls).__new__(cls, *args, **kwargs)

    @abstractmethod
    def run_import(self):
        """
        The main function that does all the importing
        """

        pass
