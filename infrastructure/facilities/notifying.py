from functools import wraps
from abc import ABCMeta, abstractmethod

from infrastructure.context import function_using_current_job, context


class BaseNotifier(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, *args, **kwargs):
        pass

    @abstractmethod
    def notify(self, recipients, message):
        pass

    def notify_dev_team_for_job_completion(self):
        self.notify(["dev_team"], "Job complete!")


@context.register_job_wrapper
def notify_dev_team_for_job_completion(func):
    @wraps(func)
    @function_using_current_job("notifier")
    def decorated(notifier, *args, **kwargs):
        try:
            return func(*args, **kwargs)
        finally:
            notifier.notify_dev_team_for_job_completion()

    return decorated


@context.register_job_facility_factory("notifier")
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
