from functools import wraps
from abc import ABCMeta

import utils


"""
Allow facilities to transparently gather metrics and meta-data, by controlling
what global state is accessible to jobs(eg importing), and operations(eg fetch,
load, save).

A Context has a stack of Jobs.
    A Job isolates and ties information gathered for a job run.
A Job has a stack of JobSteps.
    A JobStep provides the ability to structure the information hierarchically.
"""


class Context(object):
    """
    An orchestrator of various facilities (logging, profiling, etc), that makes
    the gathering of various meta-data transparent to the actual jobs, provided
    that the code denotes the start/end of a job, and of significant job steps
    """
    def __init__(self):
        # We use a Job stack to provide the facilities in a way that we don't
        # tie global state to a specific instance. We don't expect to have
        # more than one Job here, except in a case we want to run a Job within
        # a Job, and want to keep the reporting sepearate to each Job.
        self.job_stack = []
        # Automatic attributes to add to a new Job. These factories are
        # registered by the Context.register_job_facility_factory decorator
        self.job_facilities_factories = {}
        # Automatic wrappers for each job step, that want to gather information
        # about the runtime of a step. These wrappers are registered by the
        # Context.register_job_step_wrapper and
        # Context.register_job_step_method_wrapper
        self.job_step_wrappers = []
        self.job_step_method_wrappers = []
        # Automatic wrappers for each job  that want to gather information
        # about the runtime of a job. These wrappers are registered by the
        # Context.register_job_wrapper
        self.job_wrappers = []

    def new_job(self):
        """
        Create a new Job, using the registered facilities
        """
        job = Job(self)

        for attribute_name, attribute_factory in \
                self.job_facilities_factories.iteritems():
            attribute = attribute_factory(job)
            setattr(job, attribute_name, attribute)

        return job

    def _push(self, job):
        self.job_stack.append(job)

    def _pop(self):
        return self.job_stack.pop()

    @property
    def current_job(self):
        return self.job_stack[-1]

    def register_job_facility_factory(self, attribute_name):
        def decorator(type_or_factory):
            self.job_facilities_factories[attribute_name] = type_or_factory

            return type_or_factory

        return decorator

    def register_job_wrapper(self, wrapper):
        self.job_wrappers.append(wrapper)

        return wrapper

    def register_job_step_wrapper(self, wrapper):
        self.job_step_wrappers.append(wrapper)

        return wrapper

    def register_job_step_method_wrapper(self, wrapper):
        self.job_step_method_wrappers.append(wrapper)

        return wrapper

    def decorate_job(self, func):
        """
        A decorator to wrap a job (that is a function or static method) with
        the context's registered decorators.

        Because order of imports matters in Python, you should use the
        late-binding stand-alone decorator create_for_job, so that the step is
        wrapped when it's called.
        """
        decorated = func
        for wrapper in self.job_wrappers:
            decorated = wrapper(decorated)

        return decorated

    def job_step(self, func):
        """
        A decorator to wrap a step (that is a function or static method) with
        the context's registered decorators.

        Because order of imports matters in Python, you should use the
        late-binding stand-alone decorator job_step, so that the step is
        wrapped when it's called.
        """
        decorated = func
        for wrapper in self.job_step_wrappers:
            decorated = wrapper(decorated)

        decorated = creating_job_step(decorated)

        return decorated

    def job_step_method(self, func):
        """
        A decorator to wrap a step (that is an instance or class method) with
        the context's registered decorators.

        Because order of imports matters in Python, you should use the
        late-binding stand-alone decorator job_step, so that the step is
        wrapped when it's called.
        """
        decorated = func
        for wrapper in self.job_step_method_wrappers:
            decorated = wrapper(decorated)

        decorated = creating_job_step(decorated)

        return decorated


"""Global variable for context"""
context = Context()


class Job(object):
    """
    Created by Context, it holds all the facilities tied to a specific job.
    It should be accessed by context.current_job.

    It works as a context manager, and is available as a wrapper, by using
    create_for_job.

    It keeps a stack trace of JobSteps, that the various facilities can use to
    keep information hierarchically.
    """
    def __init__(self, context):
        self.context = context
        self.job_steps = []

        self._push(JobStep(self, None, "<root>"))

    def __enter__(self):
        self.context._push(self)

        return self

    def __exit__(self, _type, value, traceback):
        popped = self.context._pop()
        assert popped == self, "Popped job was not the same as pushed"

    def _push(self, job_step):
        self.job_steps.append(job_step)

    def _pop(self, expetcted):
        popped = self.job_steps.pop()
        assert popped == expetcted, "Popped job_step was not same as pushed"

    @property
    def current_section(self):
        return self.job_steps[-1]

    def new_job_step(self, name):
        """
        A new JobStep, added in the stack when used as a context manager:
        with job.new_job_step():
            pass
        """
        return JobStep(self, self.current_section, name)


class JobStep(object):
    """
    A job step, used by facilities to keep information hierarchically, as it
    is denoted by the developer, that the wrapped code constitutes a single
    step in the process.

    It works as a context manager, and is available as a wrapper, by using
    job_step.

    It doesn't serve any other purpose, other than that.
    """
    def __init__(self, job, parent, name):
        self.job = job
        self.parent = parent
        if self.parent:
            self.parents = self.parent.parents + (self.parent,)
        else:
            self.parents = ()

        self.name = name
        if self.parent:
            self.full_name = "%s/%s" % (self.parent.full_name, self.name)
        else:
            self.full_name = "%s" % self.name

        self.job_steps = []

    def __enter__(self):
        self.job._push(self)

    def __exit__(self, _type, value, traceback):
        self.job._pop(self)


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

    def __init__(self, func):
        self.func = func

        self.self_or_cls = None
        self.before_funcs = tuple()
        self.finally_funcs = tuple()

    def _copy(self, **overrides):
        wrapper = JobWrapper(self.func)
        wrapper.self_or_cls = self.self_or_cls
        wrapper.before_funcs = self.before_funcs
        wrapper.finally_funcs = self.finally_funcs
        for key, value in overrides.iteritems():
            setattr(wrapper, key, value)

        return wrapper

    def bind(self, self_or_cls):
        """
        Bind the instance to an instance or class. This is necessary if you
        want to add before and finally functions
        """

        return self._copy(self_or_cls=self_or_cls)

    def with_before(self, *before_funcs):
        """
        Run functions just before calling the main function
        """

        return self._copy(before_funcs=before_funcs + self.before_funcs)

    def with_finally(self, *finally_funcs):
        """
        Run functions just after the main function is called regardless of
        exceptions
        """

        return self._copy(finally_funcs=self.finally_funcs + finally_funcs)

    def __call__(self, *args, **kwargs):
        return self.call(*args, **kwargs)

    def call(self, *args, **kwargs):
        decorated_with_context = self._decorate_func()
        with context.new_job() as job:
            self._call_before_funcs(job)
            try:
                if self.self_or_cls:
                    return decorated_with_context(self.self_or_cls, *args, **kwargs)
                else:
                    return decorated_with_context(*args, **kwargs)
            finally:
                self._call_finally_funcs(job)

    def _decorate_func(self):
        return context.decorate_job(self.func)

    def _call_before_funcs(self, job):
        for before_func in self.before_funcs:
            before_func(job)

    def _call_finally_funcs(self, job):
        for finally_func in self.finally_funcs:
            finally_func(job)


def create_for_job(func):
    """
    Wrapper that runs the func inside a Job
    """

    return JobWrapper(func)


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


def job_step_method(func):
    """
    The late-bindind decorator version of Context.job_step_method.

    Use this so that the step is always wrapped using facilities that where
    loaded after your step was declared.
    """
    @wraps(func)
    def decorated(*args, **kwargs):
        decorated_with_context = context.job_step_method(func)

        return decorated_with_context(*args, **kwargs)

    return decorated
