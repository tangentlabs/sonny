from sonny.utils import get_config_module

from sonny.infrastructure.context import helpers

from sonny.infrastructure.facilities.base import Facility


@helpers.register_facility("config")
class Config(Facility):
    def enter_job(self, job, facility_settings):
        super(Config, self).enter_job(job, facility_settings)

        self.config_module_name, self.config = get_config_module()

    def __getattr__(self, key):
        return getattr(self.__getattribute__("config"), key)
