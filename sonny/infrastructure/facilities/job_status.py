import sys
import warnings

from functools import wraps

from sonny.infrastructure.context import helpers

from sonny.infrastructure.facilities.base import Facility


@helpers.register_facility("job_status")
class JobStatus(Facility):
    class FacilitySettings(Facility.FacilitySettings):
        filter_warnings = []
        """
        Entries to the warnings filter table
        """

    def enter_job(self, job, facility_settings):
        super(JobStatus, self).enter_job(job, facility_settings)

        self.errors = []
        self._setup_warnings()

    def exit_job(self, job, exc_type, exc_value, traceback):
        if not self.job.test:
            self.job.dashboard.submit_job_profiling()

        self._reset_warnings()

    def first_step(self, job):
        if not self.job.test:
            self.job.dashboard.register_job_start()

    def last_step(self, step, exc_type, exc_value, traceback):
        if exc_type:
            self.error(exc_type, exc_value, traceback)

        if not self.job.test:
            succeeded = (exc_type, exc_value, traceback) == (None, None, None)
            self.job.dashboard.register_job_end(succeeded)

        self.job.notifier.notify(["dev_team"],
                                 "Job '%s' completed with %s errors!" %
                                 (self.job.name, len(self.errors)))

        self.job.push_notifier.notify(self.job.push_notification_registry, self.job, self.errors)

    def error(self, exc_type, exc_value, traceback, message=None):
        if self._update_last_exception_message(exc_value, message):
            return

        step = self.job.current_step
        self.errors.append((step.name, (exc_type, exc_value, traceback), message))
        self.job.logger.error("Step '%s' raised '%s'", step.name, exc_type.__name__,
                              exception=exc_value, traceback=traceback)

    def _update_last_exception_message(self, exc_value, message):
        if not self.errors:
            return False

        step, (exc_type, last_exc_value, traceback), last_message = \
            self.errors[-1]
        if last_exc_value != exc_value:
            return False

        self.errors[-1] = step, (exc_type, exc_value, traceback), last_message
        return True

    def _setup_warnings(self):
        self._catch_warnings = warnings.catch_warnings()
        self._catch_warnings.__enter__()
        try:
            for warning in self.facility_settings.filter_warnings:
                warnings.filterwarnings(**warning)
        except Exception:
            self._reset_warnings()
            raise

    def _reset_warnings(self):
        self._catch_warnings.__exit__(None, None, None)


def error_on_exception(message):
    @wraps(error_on_exception)
    def decorator(func):
        @wraps(func)
        def decorated(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as exc_value:
                exc_type, _, traceback = sys.exc_info()
                job = helpers.get_current_job()
                job.job_status.error(exc_type, exc_value, traceback, message)

        return decorated

    return decorator
