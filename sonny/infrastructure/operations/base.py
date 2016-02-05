from abc import ABCMeta

from sonny.infrastructure.context import helpers

from sonny.infrastructure.facilities.mocking import Mockable


class BaseOperation(Mockable):
    __metaclass__ = ABCMeta

    class OperationSettings(object):
        __job_settings_name__ = None
        """
        The name to lookup in job.job_settings
        """

    def __init__(self):
        self._get_operation_settings()

    def _get_operation_settings(self):
        if not self.OperationSettings.__job_settings_name__:
            return

        job = helpers.get_current_job()
        job_settings = job.job_settings
        self.OperationSettings = getattr(
            job_settings, self.OperationSettings.__job_settings_name__,
            self.OperationSettings)
