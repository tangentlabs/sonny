from functools import wraps

from infrastructure.context import helpers

from infrastructure.facilities.base import Facility


@helpers.register_facility("job_status")
class JobStatus(Facility):
    def enter_job(self, job, facility_settings):
        super(JobStatus, self).enter_job(job, facility_settings)

        self.errors = []

    def last_step(self, step, exc_type, exc_value, traceback):
        if exc_type:
            self.error(step, (exc_type, exc_value, traceback))

        self.job.notifier.notify(["dev_team"],
                                 "Job '%s' completed with %s errors!" %
                                 (self.job.name, len(self.errors)))

    def error(self, step, (exc_type, exc_value, traceback), message=None):
        self.errors.append((step.name, (exc_type, exc_value, traceback), message))
        self.job.logger.error("Step '%s' raised '%s'", step.name, exc_type.__name__,
                              exception=exc_value, traceback=traceback)

    def message_for_exception(self, exc_value, message):
        if not self.errors:
            self.error(None, (None, None, None), message)
            return

        step, (exc_type, last_exc_value, traceback), last_message = self.errors[-1]

        if last_exc_value == exc_value:
            self.errors[-1] = step, (exc_type, exc_value, traceback), last_message
        else:
            self.error(None, (None, None, None), message)


def error_on_exception(message):
    @wraps(error_on_exception)
    def decorator(func):
        @wraps(func)
        def decorated(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                job = helpers.get_current_job()
                job.job_status.message_for_exception(e, message)

        return decorated

    return decorator
