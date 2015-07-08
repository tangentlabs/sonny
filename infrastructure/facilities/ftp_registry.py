import utils

from infrastructure.context import \
    function_using_current_job, method_using_current_job, context


class BaseFtpRegistry(object):
    @utils.must_be_implemented_by_subclasses
    def __init__(self, *args, **kwargs):
        pass

    @utils.must_be_implemented_by_subclasses
    def __getitem__(self, key):
        pass


@context.register_job_facility_factory("ftp_registry")
class FtpRegistry(BaseFtpRegistry):
    def __init__(self, job):
        self._ftp_registry = None

    @method_using_current_job("config")
    def _get_ftp_registry(self, config):
        return config.ftp_registry

    @property
    def ftp_registry(self):
        if self._ftp_registry is None:
            self._ftp_registry = self._get_ftp_registry()

        return self._ftp_registry

    def __getitem__(self, key):
        return self.ftp_registry[key]
