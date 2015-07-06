import time
from functools import wraps

import utils
from context import \
    function_using_current_job, method_using_current_job, context


class ProfilerContextManager(object):
    def __init__(self, profiler, name):
        self.profiler = profiler
        self.name = name

    def __enter__(self):
        self.profiler.section_start(self.name)

        return self.profiler

    def __exit__(self, _type, value, traceback):
        self.profiler.section_end(self.name)


class BaseProfiler(object):
    @utils.not_implemented
    def __init__(self, *args, **kwargs):
        pass

    @utils.not_implemented
    def section_start(self, name):
        pass

    @utils.not_implemented
    def section_end(self, name):
        pass

    def section(self, name):
        return ProfilerContextManager(self, name)


def profile(func):
    @wraps(func)
    @function_using_current_job("profiler")
    def decorated(profiler, *args, **kwargs):
        with profiler.section(utils.get_callable_name(func)):
            return func(*args, **kwargs)

    return decorated


def profile_method(func):
    @wraps(func)
    @method_using_current_job("profiler")
    def decorated(self_or_cls, profiler, *args, **kwargs):
        with profiler.section(utils.get_callable_name(func)):
            return func(self_or_cls, *args, **kwargs)

    return decorated


@context.auto_job_attribute("profiler")
class SimpleProfiler(BaseProfiler):
    def __init__(self):
        self._profiled = []
        self._profiling = []

    def section_start(self, name):
        profile_data = (name, time.time())
        self._profiling.append(profile_data)

    def section_end(self, expected_name):
        time_end = time.time()
        name, time_start = self._profiling.pop()
        assert name == expected_name
        duration = time_end - time_start

        self._profiled.append((name, duration))
