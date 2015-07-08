from functools import wraps

import utils
from infrastructure.context import \
    function_using_current_job, method_using_current_job, context


class BaseLogger(object):
    @utils.must_be_implemented_by_subclasses
    def __init__(self, *args, **kwargs):
        pass

    @utils.must_be_implemented_by_subclasses
    def debug(self, *args, **kwargs):
        pass

    @utils.must_be_implemented_by_subclasses
    def info(self, *args, **kwargs):
        pass

    @utils.must_be_implemented_by_subclasses
    def warn(self, *args, **kwargs):
        pass

    @utils.must_be_implemented_by_subclasses
    def error(self, *args, **kwargs):
        pass


@context.register_job_step_wrapper
def log_call(func):
    @function_using_current_job("logger")
    @wraps(func)
    def decorated(logger, *args, **kwargs):
        logger.debug('** Calling: %s with *%s, **%s',
                     utils.get_callable_name(func), args, kwargs)
        return func(*args, **kwargs)

    return decorated


@context.register_job_step_method_wrapper
def log_method_call(func):
    @method_using_current_job("logger")
    @wraps(func)
    def decorated(self_or_cls, logger, *args, **kwargs):
        logger.debug('** Calling: %s with *%s, **%s',
                     utils.get_callable_name(func), args, kwargs)
        return func(self_or_cls, *args, **kwargs)

    return decorated


@context.register_job_facility_factory("logger")
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
