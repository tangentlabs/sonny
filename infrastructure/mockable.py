from context import method_using_current_job, context


@context.auto_job_attribute("mock_registry")
class MockRegistry(object):
    def __init__(self, job):
        self.mocks = {}
        self._job = job

    def register_mock(self, _type, mocked):
        self.mocks[_type] = mocked

        return self

    def register_mocks_using_default_noops(self, *types):
        for _type in types:
            mocked = _type._default_noop
            self.register_mock(_type, mocked)

    def should_mock(self, _type):
        mocked = self.mock(_type)
        return _type != mocked

    def mock(self, _type):
        try:
            return self.mocks[_type]
        except (TypeError, KeyError):
            return _type


class Mockable(object):
    @method_using_current_job("mock_registry")
    def __new__(cls, mock_registry, *args, **kwargs):
        if mock_registry.should_mock(cls):
            mocked = mock_registry.mock(cls)
            return mocked(*args, **kwargs)
        else:
            return object.__new__(cls, *args, **kwargs)

    @classmethod
    def register_default_noop(cls, _type):
        cls._default_noop = _type
