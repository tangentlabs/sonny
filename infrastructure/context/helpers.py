from functools import wraps
from abc import ABCMeta

import utils

from infrastructure.context import core

"""
Various helper functions that make using context easier. It is mostly
decorators, that either inject a variable in the calling function/method, or
trigger an action on the context itself.

They are not necessary, but greatly reduce boilerplate, and standarise the
usage of the framework.
"""


"""Global variable for context"""
context = core.Context()


def creating_job_step(func):
    """
    Wraps a step inside a new JobStep
    """
    @function_using_current_job
    @wraps(func)
    def decorated(job, *args, **kwargs):
        with job.new_job_step(utils.get_callable_name(func)):
            return func(*args, **kwargs)

    return decorated


def function_using_current_job(*attributes):
    """
    Helper wrapper (for function and static methods), that injects the current
    job (context.current_job), or the list of requested job attributes, if they
    are provided:

    @function_using_current_job
    def f(job, a, b):
        pass

    @function_using_current_job("logger", "profiler")
    def g(logger, profiler, a, b):
        pass
    """
    def decorator(func):
        @wraps(func)
        def decorated(*args, **kwargs):
            job = context.current_job
            if attributes:
                job_args = tuple(
                    getattr(job, attribute)
                    for attribute in attributes
                )
            else:
                job_args = (job,)
            injected_args = job_args + args
            return func(*injected_args, **kwargs)

        return decorated

    if utils.is_argumentless_decorator(attributes):
        func = attributes[0]
        attributes = tuple()
        return decorator(func)
    else:
        return decorator


def method_using_current_job(*attributes):
    """
    Helper wrapper (for instance and class methods), that injects the current
    job (context.current_job), or the list of requested job attributes, if they
    are provided:

    @function_using_current_job
    def f(job, a, b):
        pass

    @function_using_current_job("logger", "profiler")
    def g(logger, profiler, a, b):
        pass
    """
    def decorator(func):
        @wraps(func)
        def decorated(self_or_cls, *args, **kwargs):
            job = context.current_job
            if attributes:
                job_args = tuple(
                    getattr(job, attribute)
                    for attribute in attributes
                )
            else:
                job_args = (job,)
            injected_args = job_args + args
            return func(self_or_cls, *injected_args, **kwargs)

        return decorated

    if utils.is_argumentless_decorator(attributes):
        func = attributes[0]
        attributes = tuple()
        return decorator(func)
    else:
        return decorator


class JobWrapper(object):
    """
    Helper wrapper around a function in a Job

    It allows before functions, and finally functions, to be called around the
    job run
    """

    __name__ = 'JobWrapper'

    def __init__(self, func, test):
        self.func = func
        self.test = test

    def __call__(self, *args, **kwargs):
        return self.call(*args, **kwargs)

    def call(self, *args, **kwargs):
        decorated_with_context = self._decorate_func()
        with context.new_job(test=self.test):
            return decorated_with_context(*args, **kwargs)

    def _decorate_func(self):
        return context.decorate_job(self.func)


def create_for_job(func):
    """
    Wrapper that runs the func inside a Job
    """

    return JobWrapper(func, test=False)


def create_for_test_job(func):
    """
    Wrapper that runs the func inside a test Job
    """

    return JobWrapper(func, test=True)


def register_current_job_importer(func):
    """
    Attach the importer instance to the Job
    """

    @wraps(func)
    @method_using_current_job
    def decorated(self_or_cls, job, *args, **kwargs):
        if type(self_or_cls) in (type(object), ABCMeta):
            cls = self_or_cls
            importer_class = cls
        else:
            self = self_or_cls
            importer_class = type(self)

        if getattr(job, 'importer_class', None):
            raise Exception("Attempting to register run two importers in same "
                            "job: %s, while running %s" %
                            (importer_class.__name__,
                             job.importer_class.__name__))

        job.importer_class = importer_class

        return func(self_or_cls, *args, **kwargs)

    return decorated


def job_step(func):
    """
    The late-bindind decorator version of Context.job_step.

    Use this so that the step is always wrapped using facilities that where
    loaded after your step was declared.
    """
    @wraps(func)
    def decorated(*args, **kwargs):
        decorated_with_context = context.job_step(func)

        return decorated_with_context(*args, **kwargs)

    return decorated


def get_helpers_mixin():
    """
    Create a mixin subclassing all the helper mixins registered with this
    context.

    It is better to use this function, instead of context.get_helpers_mixin,
    for better protability
    """
    return context.get_helpers_mixin()


def register_job_facility_factory(attribute_name):
    return context.register_job_facility_factory(attribute_name)


def register_importer_helper_mixin(cls):
    return context.register_importer_helper_mixin(cls)


def register_job_step_wrapper(wrapper):
    return context.register_job_step_wrapper(wrapper)


def register_job_wrapper(wrapper):
    return context.register_job_wrapper(wrapper)
