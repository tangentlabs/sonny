from functools import wraps

from tangent_importer.utils import get_callable_name

from tangent_importer.infrastructure.context.core import context, Job


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
        job_args = {
            "name": get_importer_name(args),
            "uuid": get_importer_uuid(args),
            "job_settings": get_importer_job_settings(args),
            "test": test,
        }
        with with_job(**job_args) as job:
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


def ignore_exceptions(classes=(Exception,), returning=None):
    """
    Ignore any exceptions raised from the function call
    """
    @wraps(ignore_exceptions)
    def decorator(func):
        @wraps(func)
        def decorated(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except classes:
                return returning

        return decorated

    return decorator


def get_importer(args):
    from tangent_importer.import_jobs.base import Importer

    if args and isinstance(args[0], Importer):
        importer = args[0]
        return importer

    return None


def get_importer_job_settings(args):
    importer = get_importer(args)
    return importer and importer.JobSettings


def get_importer_name(args):
    importer = get_importer(args)
    return importer and importer.name


def get_importer_uuid(args):
    importer = get_importer(args)
    return importer and importer.uuid


def find_facility_by_class_name(name):
    return context.find_facility_by_class_name(name)


def get_facility_settings_for_job(job_settings, facility_class):
    return Job._get_facility_settings_from_job(job_settings, facility_class)
