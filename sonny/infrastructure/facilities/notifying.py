from abc import ABCMeta, abstractmethod

from sonny.infrastructure.context import helpers

from sonny.infrastructure.facilities.base import Facility


class BaseNotifier(Facility):
    __metaclass__ = ABCMeta

    def exit_job(self, job, exc_type, exc_value, traceback):
        if job.test:
            print '********* NOTIFYING: *********'
            print self

    @abstractmethod
    def notify(self, recipients, message):
        pass


@helpers.register_facility("notifier")
class InMemoryNotifier(BaseNotifier):
    def enter_job(self, job, facility_settings):
        super(InMemoryNotifier, self).enter_job(job, facility_settings)

        self.notifications = {}

    def notify(self, recipients, message):
        for recipient in recipients:
            self.notifications.setdefault(recipient, [])\
                .append(message[:80])

    def __str__(self):
        return '\n'.join(
            '\n'.join(('To %s:' % recipient,) +
                      tuple(' * %s' % notification
                      for notification in notifications))
            for recipient, notifications
            in self.notifications.iteritems()
        )
