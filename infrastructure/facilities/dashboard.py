import json
import requests

from infrastructure.context import helpers

from infrastructure.facilities.base import Facility


class DashboardActionsMixin(object):
    def register_job_start(self):
        self.job.run_id = None

        try:
            ok, response = self.post("jobs/api/job_start/", {
                'name': self.job.name,
                'uuid': self.job.uuid,
            })
        except Exception:
            ok, response = False, None

        if not ok:
            self.job.logger.error(
                "Could not register job start to dashboard: name=%s uuid=%s",
                self.job.name, self.job.uuid)
            return False

        response = response
        self.job.run_id = response['job_run_id']

        return True

    def register_job_end(self, succeeded):
        if not self.job.run_id:
            return False

        try:
            ok, response = self.post("jobs/api/job_end/", {
                'job_run': self.job.run_id,
                'succeeded': succeeded,
            })
        except Exception:
            ok, response = False, None

        if not ok:
            self.job.logger.error(
                "Could not register job end to dashboard: name=%s uuid=%s "
                "run=%s",
                self.job.name, self.job.uuid, self.job_run_id)
            return False

        return True

    def submit_job_profiling(self):
        if not self.job.run_id:
            return False

        try:
            ok, response = self.post("jobs/api/job_profiling/", {
                'job_run': self.job.run_id,
                'profiling_json': json.dumps(self.job.profiler.profiling_section.as_dict()),
            })
        except Exception:
            ok, response = False, None

        if not ok:
            self.job.logger.error("Could not register job profiling to "
                                  "dashboard: name=%s uuid=%s run=%s",
                                  self.job.name, self.job.uuid, self.job.run_id)
            return False

        return True


@helpers.register_facility("dashboard")
class Dashboard(DashboardActionsMixin, Facility):
    def enter_job(self, job, facility_settings):
        super(Dashboard, self).enter_job(job, facility_settings)

        self._dashboard_url = None

    def exit_job(self, job, exc_type, exc_value, traceback):
        self.submit_job_profiling()

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
            self.job.logger.error("Could not connect to dashboard", exception=e)
            raise

        if response.ok:
            try:
                return True, json.loads(response.content)
            except Exception:
                pass

        return False, response.content
