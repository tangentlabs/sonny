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
        # Mixin helper classes for job classes, that provide some helper
        # methods to the class that subclasses context.get_helpers_mixin()
        self.importer_helper_mixins = []

    def new_job(self, test):
        """
        Create a new Job, using the registered facilities
        """
        job = Job(self, test=test)

        attributes = {
            attribute_name: attribute_factory(job)
            for attribute_name, attribute_factory
            in self.job_facilities_factories.iteritems()
        }
        job._add_attributes(attributes)
        if attributes:
            combined_context_manager = \
                utils.combine_context_managers(job, *attributes.itervalues())
            return combined_context_manager
        else:
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

    def register_importer_helper_mixin(self, cls):
        self.importer_helper_mixins.append(cls)

    def get_helpers_mixin(self):
        """
        Create a mixin subclassing all the helper mixins registered with this
        context.

        It is better to use the get_helpers_mixin defined in this module, for
        better portability
        """
        super_mixin = type('ContextHelpersMixin',
                           tuple(self.importer_helper_mixins),
                           {})

        return super_mixin

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
        from infrastructure.context import helpers

        decorated = func
        for wrapper in self.job_step_wrappers:
            decorated = wrapper(decorated)

        decorated = helpers.creating_job_step(decorated)

        return decorated

    def job_step_method(self, func):
        """
        A decorator to wrap a step (that is an instance or class method) with
        the context's registered decorators.

        Because order of imports matters in Python, you should use the
        late-binding stand-alone decorator job_step, so that the step is
        wrapped when it's called.
        """
        from infrastructure.context import helpers

        decorated = func
        for wrapper in self.job_step_method_wrappers:
            decorated = wrapper(decorated)

        decorated = helpers.creating_job_step(decorated)

        return decorated


class Job(object):
    """
    Created by Context, it holds all the facilities tied to a specific job.
    It should be accessed by context.current_job.

    It works as a context manager, and is available as a wrapper, by using
    create_for_job.

    It keeps a stack trace of JobSteps, that the various facilities can use to
    keep information hierarchically.
    """
    def __init__(self, context, test):
        self.context = context
        self.job_steps = []
        self.test = test

        self._push(JobStep(self, None, "<root>"))

    def _add_attributes(self, attributes):
        self.__dict__.update(attributes)

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
