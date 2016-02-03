import json
import requests

from tangent_importer.infrastructure.context import helpers

from tangent_importer.infrastructure.facilities.base import Facility


class DashboardActionsMixin(object):
    class URLS:
        JOB_REGISTER = "jobs/api/register/"
        JOB_RUN_START = "jobs/runs/api/start/"
        JOB_RUN_END = "jobs/runs/api/end/"
        JOB_RUN_PROFILING = "jobs/runs/api/profiling/"

    def register_job_start(self):
        self.job.run_id = None

        try:
            ok, response = self.post(self.URLS.JOB_RUN_START, {
                'name': self.job.name,
                'uuid': self.job.uuid,
            })
        except Exception:
            ok, response = False, None

        if not ok:
            self.job.logger.warn(
                "Could not register job start to monitoring dashboard: "
                "name=%s uuid=%s response=%s",
                self.job.name, self.job.uuid, response)
            return False

        response = response
        self.job.run_id = response['job_run_id']

        return True

    def register_job_end(self, succeeded):
        if not self.job.run_id:
            return False

        try:
            ok, response = self.post(self.URLS.JOB_RUN_END, {
                'job_run': self.job.run_id,
                'succeeded': succeeded,
            })
        except Exception:
            ok, response = False, None

        if not ok:
            self.job.logger.warn(
                "Could not register job end to monitoring dashboard: name=%s "
                "uuid=%s run=%s response=%s",
                self.job.name, self.job.uuid, self.job_run_id, response)
            return False

        return True

    def submit_job_profiling(self):
        if not self.job.run_id:
            return False

        try:
            profiling = self.job.profiler.profiling_section.as_dict()
            ok, response = self.post(self.URLS.JOB_RUN_PROFILING, {
                'job_run': self.job.run_id,
                'profiling_json': json.dumps(profiling),
            })
        except Exception:
            ok, response = False, None

        if not ok:
            self.job.logger.warn("Could not register job profiling to "
                                 "monitoring dashboard: name=%s uuid=%s "
                                 "run=%s response=%s",
                                 self.job.name, self.job.uuid, self.job.run_id,
                                 response)
            return False

        return True

    def discover_and_register_jobs(self):
        ok, response = False, None
        try:
            from infrastructure.discover_jobs import get_importers_details
            ok, response = self.post(self.URLS.JOB_REGISTER, {
                'jobs': json.dumps(get_importers_details()),
            })
        finally:
            if not ok:
                self.job.logger.warn("Could not register jobs to monitoring "
                                     "dashboard: name=%s uuid=%s run=%s "
                                     "response=%s",
                                     self.job.name, self.job.uuid,
                                     self.job.run_id, response)

        return True


@helpers.register_facility("dashboard")
class Dashboard(DashboardActionsMixin, Facility):
    def enter_job(self, job, facility_settings):
        super(Dashboard, self).enter_job(job, facility_settings)

        self._dashboard_url = None

    @property
    def dashboard_url(self):
        if not self._dashboard_url:
            self._dashboard_url = self.job.config.DASHBOARD_URL

        return self._dashboard_url

    def post(self, relative_url, data):
        url = '%s/%s' % (self.dashboard_url, relative_url)
        try:
            response = requests.post(url, data=data)
        except Exception, e:
            self.job.logger.warn("Could not connect to monitoring dashboard",
                                 exception=e)
            raise

        if response.ok:
            try:
                return True, json.loads(response.content)
            except Exception:
                pass

        return False, response.content
