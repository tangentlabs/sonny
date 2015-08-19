from functools import wraps
from traceback import print_tb
import warnings
from abc import ABCMeta, abstractmethod

from infrastructure.context import helpers

from infrastructure.facilities.base import Facility


class BaseLogger(Facility):
    __metaclass__ = ABCMeta

    class FacilitySettings(Facility.FacilitySettings):
        log_level = "DEBUG"
        """
        Minimum log level to output. Levels are, ascending:

        DEBUG
        INFO
        WARNING
        ERROR
        """

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"

    LOG_LEVELS = [DEBUG, INFO, WARNING, ERROR]

    def enter_job(self, job, facility_settings):
        super(BaseLogger, self).enter_job(job, facility_settings)

        log_level_lindex = self.LOG_LEVELS.index(self.facility_settings.log_level)
        self.log_level_to_print = set(self.LOG_LEVELS[log_level_lindex:])

    def exit_job(self, job, exc_type, exc_value, traceback):
        if job.test:
            print '*********** LOGS: ***********'
            print self

    def wrap_step(self, step, func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            with warnings.catch_warnings(record=True) as caught_warninings:
                try:
                    return func(*args, **kwargs)
                finally:
                    for warning in caught_warninings:
                        self.warn('%s', warning.message)

        return wrapped

    @abstractmethod
    def _log(self, level, message, args, kwargs):
        pass

    def _should_log_level(self, level):
        return level in self.log_level_to_print

    def debug(self, message, *args, **kwargs):
        self._log(self.DEBUG, message, args, kwargs)

    def info(self, message, *args, **kwargs):
        self._log(self.INFO, message, args, kwargs)

    def warn(self, message, *args, **kwargs):
        self._log(self.WARNING, message, args, kwargs)

    def error(self, message, *args, **kwargs):
        self._log(self.ERROR, message, args, kwargs)


@helpers.register_facility("logger")
class InMemoryLogger(BaseLogger):
    def enter_job(self, job, facility_settings):
        super(InMemoryLogger, self).enter_job(job, facility_settings)

        self._logs = []

    def wrap_step(self, step, func):
        func = super(InMemoryLogger, self).wrap_step(step, func)

        @wraps(func)
        def wrapped(*args, **kwargs):
            self.debug('** Calling: %s with *%s, **%s',
                       step.name, args, kwargs)
            return func(*args, **kwargs)

        return wrapped

    def _log(self, level, message, args, kwargs,
             exception=None, traceback=None):
        if not self._should_log_level(level):
            return

        log_string = str(message)
        if args:
            log_string = log_string % args
        else:
            log_string = log_string % kwargs
        section_full_name = self.job.current_step.name
        self._logs.append((level, section_full_name, log_string[:80]))

        if not self.job.test:
            self._to_stdout(level, section_full_name, log_string,
                            exception=exception, traceback=traceback)

    def _to_stdout(self, level, section_full_name, log_string,
                   exception=None, traceback=None):
            print "[%s] [%s] %s" % (level, section_full_name, log_string)
            if traceback:
                print_tb(traceback)
            if exception:
                print '%s:' % type(exception).__name__, exception

    def error(self, message, *args, **kwargs):
        if 'traceback' in kwargs:
            traceback = kwargs.pop('traceback')
        else:
            traceback = None
        if 'exception' in kwargs:
            exception = kwargs.pop('exception')
        else:
            exception = None
        self._log("ERROR", message, args, kwargs,
                  exception=exception, traceback=traceback)

    def __str__(self):
        return '\n'.join(
            "[%s] [%s] %s" % (level, section_full_name, log_string)
            for level, section_full_name, log_string in self._logs
        )
