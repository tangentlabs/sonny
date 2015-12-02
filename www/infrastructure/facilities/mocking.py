from infrastructure.context import helpers

from infrastructure.facilities.base import Facility


@helpers.register_facility("mock_registry")
class MockRegistry(Facility):
    class FacilitySettings(Facility.FacilitySettings):
        mock_classes = []
        """
        List of class names to register for mocking on startup. The class name
        can either be fully or partially qualified, eg either of those wokrs:

        CustomOperation
        custom.CustomOperation
        infrastructure.operations.custom.CustomOperation
        """

        no_mock_classes = []
        """
        The opposite of mock_classes: don't mock these classes. This supersedes
        mock_classes
        """

    auto_mocks_for_local_testing = set()
    """
    Classes that should be automatically mocked when testing locally
    """

    def enter_job(self, job, facility_settings):
        super(MockRegistry, self).enter_job(job, facility_settings)

        self.mocks = {}
        if self.job.test:
            self.register_auto_mocks_for_local_testing()
        self.register_startup_mocks()
        self.unregister_startup_no_mocks()

    def register_mock(self, _type, mocked):
        self.mocks[_type] = mocked

        return self

    def unregister_mock(self, _type):
        if _type in self.mocks:
            del self.mocks[_type]

    def register_mocks_using_default_noops(self, *types):
        for _type in types:
            mocked = _type._default_noop
            self.register_mock(_type, mocked)

    def unregister_mocks(self, *types):
        for _type in types:
            self.unregister_mock(_type)

    def register_auto_mocks_for_local_testing(self):
        self.register_mocks_using_default_noops(
            *self.auto_mocks_for_local_testing)

    def register_startup_mocks(self):
        types = [
            _type
            for _type in self.auto_mocks_for_local_testing
            if _type.__name__
            in self.facility_settings.mock_classes
        ]
        self.register_mocks_using_default_noops(*types)

    def unregister_startup_no_mocks(self):
        types = [
            _type
            for _type in self.auto_mocks_for_local_testing
            if _type.__name__
            in self.facility_settings.no_mock_classes
        ]
        self.unregister_mocks(*types)

    def should_mock(self, _type):
        mocked = self.mock(_type)
        return _type != mocked

    def mock(self, _type):
        try:
            return self.mocks[_type]
        except (TypeError, KeyError):
            return _type

    @classmethod
    def auto_mock_for_local_testing(cls, _type):
        cls.auto_mocks_for_local_testing.add(_type)

        return _type


class Mockable(object):
    def __new__(cls, *args, **kwargs):
        job = helpers.get_current_job()
        if job.mock_registry.should_mock(cls):
            mocked = job.mock_registry.mock(cls)
            return mocked(*args, **kwargs)
        else:
            return object.__new__(cls, *args, **kwargs)

    @classmethod
    def register_default_noop(cls, _type):
        cls._default_noop = _type

        return _type

    @classmethod
    def auto_mock_for_local_testing(cls, _type):
        return MockRegistry.auto_mock_for_local_testing(_type)
