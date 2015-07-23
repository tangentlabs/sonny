from abc import ABCMeta, abstractmethod

from infrastructure.context import helpers

from infrastructure.facilities.base import BaseFacility


class BaseRegistry(BaseFacility):
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, *args, **kwargs):
        pass

    @abstractmethod
    def __getitem__(self, key):
        pass


class GenericConfigRegistry(BaseRegistry):
    __metaclass__ = ABCMeta

    registry_config_name = None
    """
    The name of the atrtribute to get from config
    """

    def __init__(self, job):
        self._registry = None

    @helpers.using_current_job("config")
    def _get_registry(self, config):
        return getattr(config, self.registry_config_name)

    @property
    def registry(self):
        if self._registry is None:
            self._registry = self._get_registry()

        return self._get_registry()

    def __getitem__(self, key):
        return self.registry[key]
