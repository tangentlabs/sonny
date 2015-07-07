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
    def job_step(self, name):
        pass


@context.register_job_step_wrapper
def profile(func):
    @function_using_current_job("profiler")
    @wraps(func)
    def decorated(profiler, *args, **kwargs):
        with profiler.job_step(utils.get_callable_name(func)):
            return func(*args, **kwargs)

    return decorated


@context.register_job_step_method_wrapper
def profile_method(func):
    @method_using_current_job("profiler")
    @wraps(func)
    def decorated(self_or_cls, profiler, *args, **kwargs):
        with profiler.job_step(utils.get_callable_name(func)):
            return func(self_or_cls, *args, **kwargs)

    return decorated


class ProfilingSection(object):
    def __init__(self, profiler, job_step, name, parent, duration=None):
        self.profiler = profiler
        self.job_step = job_step
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


@context.register_job_facility_factory("profiler")
class SimpleProfiler(BaseProfiler):
    def __init__(self, job):
        self._job = job
        self.profiling_section = \
            ProfilingSection(self, self._job.current_section, "<root>", None)

    def job_step(self, name):
        profiling_section = ProfilingSection(
            self, self._job.current_section, name, self.profiling_section)

        return profiling_section

    def _push(self, profiling_section):
        assert profiling_section.parent == self.profiling_section
        self.profiling_section = profiling_section

    def _pop(self, expected_profiling_section):
        assert expected_profiling_section == self.profiling_section
        self.profiling_section = self.profiling_section.parent
