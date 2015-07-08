import utils

from infrastructure.context import \
    function_using_current_job, method_using_current_job, context


class BaseDbRegistry(object):
    @utils.must_be_implemented_by_subclasses
    def __init__(self, *args, **kwargs):
        pass

    @utils.must_be_implemented_by_subclasses
    def __getitem__(self, key):
        pass


@context.register_job_facility_factory("db_registry")
class DbRegistry(BaseDbRegistry):
    def __init__(self, job):
        self._db_registry = None

    @method_using_current_job("config")
    def _get_db_registry(self, config):
        return config.db_registry

    @property
    def db_registry(self):
        if self.db_registry is None:
            self._db_registry = self._get_db_registry()

        return self._get_db_registry

    def __getitem__(self, key):
        return self.db_registry[key]
