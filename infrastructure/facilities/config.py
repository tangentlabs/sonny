import os
from importlib import import_module

from infrastructure.context import helpers

from infrastructure.facilities.base import Facility


@helpers.register_facility("config")
class Config(Facility):
    # The environment variable name
    CONF_ENV_VAR_NAME = "IMPORT_CONF"

    def enter_job(self, job, facility_settings):
        super(Config, self).enter_job(job, facility_settings)

        self.config_environment = os.environ.get(self.CONF_ENV_VAR_NAME, "local")
        self.config = import_module('conf.%s' % self.config_environment)
        self.config.config_environment = self.config_environment

    def __getattr__(self, key):
        return getattr(self.__getattribute__("config"), key)
