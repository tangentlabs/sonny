from functools import wraps

from utils import get_callable_name

from infrastructure.context.core import context


def get_current_job():
    return context.current_job


def register_facility(name):
    def decorator(klass):
        return context.register_facility(name, klass)

    return decorator


def with_job(**kwargs):
    """
    Create a context manager for a job
    """
    return context.new_job(**kwargs)


def job(func, test=False):
    """
    Method/function decorator for running a job
    """
    @wraps(func)
    def decorated(*args, **kwargs):
        name = get_importer_name(args)
        job_settings = get_importer_job_settings(args)
        with with_job(name=name, job_settings=job_settings, test=test) as job:
            return func(*args, job=job, **kwargs)

    return decorated


def test_job(func):
    return job(func, test=True)


def with_step(**kwargs):
    """
    Create a context manager for a step
    """
    return context.current_job.new_step(**kwargs)


def step(func):
    """
    Method/function decorator for running a step
    """
    @wraps(func)
    def decorated(*args, **kwargs):
        name = get_callable_name(func)
        with with_step(name=name) as step:
            wrapped = step.wrap_step_function(func)
            return wrapped(*args, **kwargs)

    return decorated


def ignore_exceptions(returning):
    """
    Ignore any exceptions raised from the function call
    """
    @wraps(ignore_exceptions)
    def decorator(func):
        @wraps(func)
        def decorated(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception:
                return returning

        return decorated

    return decorator


def get_importer_job_settings(args):
    from import_jobs.base import Importer

    if args and isinstance(args[0], Importer):
        importer = args[0]
        return importer.JobSettings

    return None


def get_importer_name(args):
    from import_jobs.base import Importer

    if args and isinstance(args[0], Importer):
        importer = args[0]
        return importer.name

    return None
