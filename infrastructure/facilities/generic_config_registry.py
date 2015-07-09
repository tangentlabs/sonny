import utils

from infrastructure.context import \
    function_using_current_job, method_using_current_job, context


class BaseRegistry(object):
    @utils.must_be_implemented_by_subclasses
    def __init__(self, *args, **kwargs):
        pass

    @utils.must_be_implemented_by_subclasses
    def __getitem__(self, key):
        pass


class GenericConfigRegistry(BaseRegistry):
    registry_config_name = None
    """
    The name of the atrtribute to get from config
    """

    def __init__(self, job):
        self._registry = None

    @method_using_current_job("config")
    def _get_registry(self, config):
        return getattr(config, self.registry_config_name)

    @property
    def registry(self):
        if self._registry is None:
            self._registry = self._get_registry()

        return self._get_registry()

    def __getitem__(self, key):
        return self.registry[key]
