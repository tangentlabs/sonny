from functools import wraps
from abc import ABCMeta, abstractmethod

from infrastructure.context import helpers

from infrastructure.facilities.base import Facility


class BaseLogger(Facility):
    __metaclass__ = ABCMeta

    def exit_job(self, job, exc_type, exc_value, traceback):
        if job.test:
            print '*********** LOGS: ***********'
            print self

    @abstractmethod
    def _log(self, level, message, args, kwargs):
        pass

    def debug(self, message, *args, **kwargs):
        self._log("DEBUG", message, args, kwargs)

    def info(self, message, *args, **kwargs):
        self._log("INFO", message, args, kwargs)

    def warn(self, message, *args, **kwargs):
        self._log("WARN", message, args, kwargs)

    def error(self, message, *args, **kwargs):
        self._log("ERROR", message, args, kwargs)


@helpers.register_facility("logger")
class InMemoryLogger(BaseLogger):
    def enter_job(self, job, facility_settings):
        super(InMemoryLogger, self).enter_job(job, facility_settings)

        self._logs = []

    def wrap_step(self, step, func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            self.debug('** Calling: %s with *%s, **%s',
                       step.name, args, kwargs)
            return func(*args, **kwargs)

        return wrapped

    def _log(self, level, message, args, kwargs):
        if args:
            log_string = message % args
        else:
            log_string = message % kwargs
        self._logs.append((level, self.job.current_step.name, log_string))

    def __str__(self):
        return '\n'.join(
            "[%s] [%s] %s" % (level, section_full_name, log_string)
            for level, section_full_name, log_string in self._logs
        )
