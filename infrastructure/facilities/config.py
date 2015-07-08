import os
import yaml
from importlib import import_module

from infrastructure.context import \
    function_using_current_job, method_using_current_job, context


@context.register_job_facility_factory("config")
class Config(object):
    CONF_ENV_VAR_NAME = "IMPORT_CONF"

    def __init__(self, job):
        self.config_environment = os.environ.get(self.CONF_ENV_VAR_NAME, "local")
        self.config = import_module('conf.%s' % self.config_environment)

    def __getattr__(self, key):
        return getattr(self.config, key)

    def get_job_environment_config(self, job_config_filename):
        with open(job_config_filename, "rb") as _file:
            job_config = yaml.load(_file)
            job_environment_config = job_config[self.config_environment]

            return job_environment_config
