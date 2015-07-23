from functools import wraps
from abc import ABCMeta, abstractmethod

import utils

from infrastructure.context import helpers

from infrastructure.facilities.base import BaseFacility


class BaseLogger(BaseFacility):
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, *args, **kwargs):
        pass

    @helpers.method_using_current_job
    def __exit__(self, job, _type, value, traceback):
        if job.test:
            print '*********** LOGS: ***********'
            print self

    @abstractmethod
    def debug(self, *args, **kwargs):
        pass

    @abstractmethod
    def info(self, *args, **kwargs):
        pass

    @abstractmethod
    def warn(self, *args, **kwargs):
        pass

    @abstractmethod
    def error(self, *args, **kwargs):
        pass


@helpers.register_job_step_wrapper
def log_call(func):
    @helpers.function_using_current_job("logger")
    @wraps(func)
    def decorated(logger, *args, **kwargs):
        logger.debug('** Calling: %s with *%s, **%s',
                     utils.get_callable_name(func), args, kwargs)
        return func(*args, **kwargs)

    return decorated


@helpers.register_job_facility_factory("logger")
class InMemoryLogger(BaseLogger):
    def __init__(self, job):
        self._logs = []
        self._job = job

    def _log(self, level, message, args, kwargs):
        if args:
            log_string = message % args
        else:
            log_string = message % kwargs
        log_string = "[%s] %s" % (level, log_string)
        self._logs.append((self._job.current_section.full_name, log_string))

    def debug(self, message, *args, **kwargs):
        self._log("DEBUG", message, args, kwargs)

    def info(self, message, *args, **kwargs):
        self._log("INFO", message, args, kwargs)

    def warn(self, message, *args, **kwargs):
        self._log("WARN", message, args, kwargs)

    def error(self, message, *args, **kwargs):
        self._log("ERROR", message, args, kwargs)

    def __str__(self):
        return '\n'.join(
            "[%s] %s" % (section_full_name, log_string)
            for section_full_name, log_string in self._logs
        )
