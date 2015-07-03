from context import context


class MockRegistry(object):
    def __init__(self):
        self.mocks = {}

    def register_mock(self, _type, mocked):
        self.mocks[_type] = mocked

        return self

    def should_mock(self, _type):
        mocked = self.mock(_type)
        return _type != mocked

    def mock(self, _type):
        try:
            return self.mocks[_type]
        except (TypeError, KeyError):
            return _type


class Mockable(object):
    def __new__(cls, *args, **kwargs):
        mock_registry = context.current_frame.mock_registry
        if mock_registry.should_mock(cls):
            mocked = mock_registry.mock(cls)
            return mocked(*args, **kwargs)
        else:
            return object.__new__(cls, *args, **kwargs)
