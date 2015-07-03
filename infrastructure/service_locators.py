import utils


class BaseServiceLocator(object):
    @utils.not_implemented
    def __init__(self, *args, **kwargs):
        pass

    @utils.not_implemented
    def locate(self):
        pass


class SimpleServiceLocator(object):
    def __init__(self):
        pass

    def locate(self, service):
        return service


class MockServiceLocator(object):
    def __init__(self):
        self.replacements = {}

    def mock(self, type_or_func, replacement):
        self.replacements[type_or_func] = replacement

        return self

    def locate(self, service):
        try:
            replacement = self.replacements[service]
        except (TypeError, KeyError):
            replacement = service

        return replacement
