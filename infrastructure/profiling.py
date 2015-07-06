import time
from functools import wraps

import utils
from context import \
    function_using_current_job, method_using_current_job, context


class BaseProfiler(object):
    @utils.not_implemented
    def __init__(self, *args, **kwargs):
        pass

    @utils.not_implemented
    def section(self, name):
        pass


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


class ProfilingSection(object):
    def __init__(self, profiler, section, name, parent, duration=None):
        self.profiler = profiler
        self.section = section
        self.parent = parent
        if self.parent:
            self.parent.profiling_sections.append(self)
        self.name = name
        self.duration = duration

        self.profiling_sections = []

    def start(self):
        self.start_time = time.time()

    def finish(self):
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time

    def __enter__(self):
        self.profiler._push(self)
        self.start()
        return self.profiler

    def __exit__(self, _type, value, traceback):
        self.profiler._pop(self)
        self.finish()


@context.auto_job_attribute("profiler")
class SimpleProfiler(BaseProfiler):
    def __init__(self, job):
        self._job = job
        self.profiling_section = \
            ProfilingSection(self, self._job.current_section, "<root>", None)

    def section(self, name):
        profiling_section = ProfilingSection(
            self, self._job.current_section, name, self.profiling_section)

        return profiling_section

    def _push(self, profiling_section):
        assert profiling_section.parent == self.profiling_section
        self.profiling_section = profiling_section

    def _pop(self, expected_profiling_section):
        assert expected_profiling_section == self.profiling_section
        self.profiling_section = self.profiling_section.parent