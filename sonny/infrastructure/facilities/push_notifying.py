import json
import requests

from abc import ABCMeta, abstractmethod

from sonny.infrastructure.context import helpers

from sonny.infrastructure.facilities.base import Facility


class BasePushNotifier(Facility):
    __metaclass__ = ABCMeta

    def exit_job(self, job, exc_type, exc_value, traceback):
        if job.test:
            print '********* PUSH NOTIFYING: *********'
            print self

    @abstractmethod
    def notify(self, registry, job, errors):
        pass


@helpers.register_facility("push_notifier")
class PushNotifier(BasePushNotifier):
    def enter_job(self, job, facility_settings):
        super(PushNotifier, self).enter_job(job, facility_settings)

        self.notifications = []

    @helpers.step
    def notify(self, registry, job, errors):
        if registry:
            for name, push_registry in registry.registry.iteritems():
                url = push_registry["url"] + "/rest/pushNotification"
                system = push_registry["system"]
                subSystem = push_registry["subSystem"]
                title = push_registry["title"]
                body = push_registry["body"]
                icon = push_registry["icon"]
                link = push_registry["link"]
                highPriority = push_registry["highPriority"]
                ttl = push_registry["ttl"]

                data = {
                    "system": system,
                    "subSystem": subSystem,
                    "title": title,
                    "body": body % (job.name, len(errors)),
                    "icon": icon,
                    "link": link,
                    "highPriority": highPriority,
                    "ttl": ttl,
                }
                self.notifications.append(json.dumps(data))

                requests.post(url, data=json.dumps(data))

    def __str__(self):
        return '\n'.join("data: %s" % notification for notification in self.notifications)
