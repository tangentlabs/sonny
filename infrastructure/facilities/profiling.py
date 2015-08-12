import time
from functools import wraps
from abc import ABCMeta, abstractmethod

from infrastructure.context import helpers

from infrastructure.facilities.base import Facility


class BaseProfiler(Facility):
    __metaclass__ = ABCMeta

    def exit_job(self, job, exc_type, exc_value, traceback):
        if job.test:
            print '********* PROFILING: *********'
            print self

    def wrap_step(self, step, func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            with self.job_step(step.name):
                return func(*args, **kwargs)

        return wrapped

    @abstractmethod
    def job_step(self, name):
        pass


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

    def __str__(self, indent=""):
        return ''.join(
            "\n%s[%s] %s: %.3f%s" %
            (indent, profiling_section.job_step.name,
             profiling_section.name, profiling_section.duration or -1,
             profiling_section.__str__(indent="  " + indent))
            for profiling_section in self.profiling_sections
        )


@helpers.register_facility("profiler")
class SimpleProfiler(BaseProfiler):
    def enter_job(self, job, facility_settings):
        super(SimpleProfiler, self).enter_job(job, facility_settings)

        self.profiling_section = \
            ProfilingSection(self, self.job.current_step, "<root>", None)

    def job_step(self, name):
        profiling_section = ProfilingSection(
            self, self.job.current_step, name, self.profiling_section)

        return profiling_section

    def _push(self, profiling_section):
        assert profiling_section.parent == self.profiling_section
        self.profiling_section = profiling_section

    def _pop(self, expected_profiling_section):
        assert expected_profiling_section == self.profiling_section
        self.profiling_section = self.profiling_section.parent

    def __str__(self):
        return str(self.profiling_section)
