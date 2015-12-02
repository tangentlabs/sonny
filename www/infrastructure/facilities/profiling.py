import time
import resource
from abc import ABCMeta, abstractmethod

from utils import pretty_bytes

from infrastructure.context import helpers

from infrastructure.facilities.base import Facility


class BaseProfiler(Facility):
    __metaclass__ = ABCMeta

    def exit_job(self, job, exc_type, exc_value, traceback):
        if job.test:
            print '********* PROFILING: *********'
            print self

    def enter_step(self, step):
        job_step = self.job_step(step.name)
        job_step.__enter__()

    def exit_step(self, step, exc_type, exc_value, traceback):
        self.profiling_section.__exit__(exc_type, exc_value, traceback)

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
        self.memory_created = None

        self.profiling_sections = []

    def _get_memory_usage(self):
        rusage = resource.getrusage(resource.RUSAGE_SELF)
        page_size = resource.getpagesize()
        return rusage.ru_maxrss * page_size

    def start(self):
        self.start_time = time.time()
        self.start_memory = self._get_memory_usage()

    def finish(self):
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
        self.end_memory = self._get_memory_usage()
        self.memory_created = self.end_memory - self.start_memory

    def __enter__(self):
        self.profiler._push(self)
        self.start()
        return self.profiler

    def __exit__(self, _type, value, traceback):
        self.profiler._pop(self)
        self.finish()

    def __str__(self, indent=""):
        return ''.join(
            "\n%s[%s] %s: %.3fs, %s%s" %
            (indent, profiling_section.job_step.name,
             profiling_section.name, profiling_section.duration or -1,
             pretty_bytes(profiling_section.memory_created),
             profiling_section.__str__(indent="  " + indent))
            for profiling_section in self.profiling_sections
        )

    def as_dict(self):
        _dict = {
            "name": self.job_step.name if self.job_step else '<root>',
            "duration": self.duration,
            "memory": self.memory_created,
            "sections": [
                profiling_section.as_dict()
                for profiling_section in self.profiling_sections
            ],
        }

        if not self.parent:
            _dict['duration'] = sum((section.duration for section in self.profiling_sections), 0)
            _dict['memory'] = sum((section.memory_created for section in self.profiling_sections), 0)

        return _dict


@helpers.register_facility("profiler")
class SimpleProfiler(BaseProfiler):
    def enter_job(self, job, facility_settings):
        super(SimpleProfiler, self).enter_job(job, facility_settings)

        self.profiling_section = \
            ProfilingSection(self, None, "<root>", None)

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
