import os
from importlib import import_module

from tangent_importer.infrastructure.context import helpers

from tangent_importer.infrastructure.facilities.base import Facility


@helpers.register_facility("config")
class Config(Facility):
    # The environment variable name
    CONF_ENV_VAR_NAME = "IMPORT_CONF"

    def enter_job(self, job, facility_settings):
        super(Config, self).enter_job(job, facility_settings)

        self.config_module_name = \
            os.environ.get(self.CONF_ENV_VAR_NAME, "conf.local")
        try:
            self.config = import_module(self.config_module_name)
        except ImportError, e:
            raise Exception("Could not load config module '%s'. Make sure "
                            "that you specified properly in env variable %s, "
                            "and that it can be loaded:\n %s"
                            % (self.config_module_name,
                               self.CONF_ENV_VAR_NAME, e))
        self.config.environment = \
            getattr(self.config, 'environment', self.config_module_name)

    def __getattr__(self, key):
        return getattr(self.__getattribute__("config"), key)
