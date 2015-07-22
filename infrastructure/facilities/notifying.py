from functools import wraps
from abc import ABCMeta, abstractmethod

from infrastructure.context import helpers

from infrastructure.facilities.base import BaseFacility


class BaseNotifier(BaseFacility):
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, *args, **kwargs):
        pass

    @helpers.method_using_current_job
    def __exit__(self, job, _type, value, traceback):
        if job.test:
            print '********* NOTIFYING: *********'
            print self

    @abstractmethod
    def notify(self, recipients, message):
        pass

    @helpers.method_using_current_job
    def notify_dev_team_for_job_completion(self, job):
        job_name = '%s.%s' % (job.importer_class.__module__,
                              job.importer_class.__name__)
        self.notify(["dev_team"], "Job '%s' complete!" % job_name)


@helpers.register_job_wrapper
def notify_dev_team_for_job_completion(func):
    @wraps(func)
    @helpers.function_using_current_job("notifier")
    def decorated(notifier, *args, **kwargs):
        try:
            return func(*args, **kwargs)
        finally:
            notifier.notify_dev_team_for_job_completion()

    return decorated


@helpers.register_job_facility_factory("notifier")
class InMemoryNotifier(BaseNotifier):
    def __init__(self, *args, **kwargs):
        self.notifications = {}

    def notify(self, recipients, message):
        for recipient in recipients:
            self.notifications.setdefault(recipient, [])\
                .append(message)

    def __str__(self):
        return '\n'.join(
            '\n'.join(('To %s:' % recipient,) +
                      tuple(' * %s' % notification
                      for notification in notifications))
            for recipient, notifications
            in self.notifications.iteritems()
        )
