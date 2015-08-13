import yaml

from infrastructure.context import helpers

from infrastructure.facilities.base import Facility


@helpers.register_facility("job_config")
class JobConfig(Facility):
    class FacilitySettings(Facility.FacilitySettings):
        filename = None

    def enter_job(self, job, facility_settings):
        super(JobConfig, self).enter_job(job, facility_settings)

        self._config = None

    def exit_job(self, job, exc_type, exc_value, traceback):
        del self._config

    def __getitem__(self, key):
        return self.config[key]

    @property
    def config(self):
        if self._config is None:
            self._config = self._load_config()

        return self._config

    def _load_config(self):
        filename = self.facility_settings.filename
        config_environment = self.job.config.config_environment
        config = self._get_job_environment_config(filename, config_environment)

        return config

    def _get_job_environment_config(self, job_config_filename, config_environment):
        if not job_config_filename:
            return {}

        with open(job_config_filename, "rb") as _file:
            job_config = yaml.load(_file)
            job_default_config = job_config['default']
            job_environment_config = job_config[config_environment]

            complete_job_environment_config = dict(job_default_config)
            complete_job_environment_config.update(job_environment_config)

            return complete_job_environment_config
