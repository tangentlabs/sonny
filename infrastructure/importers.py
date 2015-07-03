from infrastructure.service_locators import SimpleServiceLocator


class BaseImporter(object):
    def __init__(self, locator=None):
        if locator is None:
            locator = SimpleServiceLocator()

        self.locator = locator

    def locate(self, service):
        return self.locator.locate(service)
