from functools import wraps

from utils import get_callable_name

from infrastructure.context.core import context


def get_current_job():
    return context.current_job


def register_facility(name):
    def decorator(klass):
        return context.register_facility(name, klass)

    return decorator


def job(func, test=False):
    """
    Method/function decorator for running a job
    """
    @wraps(func)
    def decorated(*args, **kwargs):
        name = get_importer_name(args)
        job_settings = get_importer_job_settings(args)
        with context.new_job(name=name, job_settings=job_settings, test=test) as job:
            return func(*args, job=job, **kwargs)

    return decorated


def test_job(func):
    return job(func, test=True)


def step(func):
    """
    Method/function decorator for running a step
    """
    @wraps(func)
    def decorated(*args, **kwargs):
        name = get_callable_name(func)
        with context.current_job.new_step(name=name) as step:
            wrapped = step.wrap_step_function(func)
            return wrapped(*args, **kwargs)

    return decorated


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
