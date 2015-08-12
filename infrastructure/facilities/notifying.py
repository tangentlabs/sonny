from functools import wraps
from abc import ABCMeta, abstractmethod

from infrastructure.context import helpers

from infrastructure.facilities.base import Facility


class BaseNotifier(Facility):
    __metaclass__ = ABCMeta

    def exit_job(self, job, exc_type, exc_value, traceback):
        self.notify_dev_team_for_job_completion()

        if job.test:
            print '********* NOTIFYING: *********'
            print self

    @abstractmethod
    def notify(self, recipients, message):
        pass

    def notify_dev_team_for_job_completion(self):
        self.notify(["dev_team"], "Job '%s' complete!" % self.job.name)


@helpers.register_facility("notifier")
class InMemoryNotifier(BaseNotifier):
    def enter_job(self, job, facility_settings):
        super(InMemoryNotifier, self).enter_job(job, facility_settings)

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
