from abc import ABCMeta

from sonny.infrastructure.facilities.base import Facility


class GenericConfigRegistry(Facility):
    __metaclass__ = ABCMeta

    registry_config_name = None
    """
    The name of the atrtribute to get from config
    """

    def enter_job(self, job, facility_settings):
        super(GenericConfigRegistry, self).enter_job(job, facility_settings)

        self._registry = None

    def _get_registry(self):
        return getattr(self.job.config, self.registry_config_name)

    @property
    def registry(self):
        if self._registry is None:
            self._registry = self._get_registry()

        return self._get_registry()

    def __getitem__(self, key):
        return self.registry[key]
