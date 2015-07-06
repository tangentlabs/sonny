from functools import wraps

import utils


class Context(object):
    def __init__(self):
        self.job_stack = []
        self.job_attribute_factories = {}
        self.section_wrappers = []
        self.method_section_wrappers = []

    def new_job(self):
        job = Job(self)

        for attribute_name, attribute_factory in \
                self.job_attribute_factories.iteritems():
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

    def auto_job_attribute(self, attribute_name):
        def decorator(type_or_factory):
            self.job_attribute_factories[attribute_name] = type_or_factory

            return type_or_factory

        return decorator

    def auto_section_wrapper(self, wrapper):
        self.section_wrappers.append(wrapper)

        return wrapper

    def auto_method_section_wrapper(self, wrapper):
        self.method_section_wrappers.append(wrapper)

        return wrapper

    def auto_section(self, func):
        decorated = func
        for wrapper in self.section_wrappers:
            decorated = wrapper(decorated)

        decorated = with_new_section(decorated)

        return decorated

    def auto_method_section(self, func):
        decorated = func
        for wrapper in self.method_section_wrappers:
            decorated = wrapper(decorated)

        decorated = with_new_section(decorated)

        return decorated


# Global context
context = Context()


class Job(object):
    def __init__(self, context):
        self.context = context
        self.sections = []

        self._push(Section(self, None, "<root>"))

    def __enter__(self):
        self.context._push(self)

        return self

    def __exit__(self, _type, value, traceback):
        popped = self.context._pop()
        assert popped == self, "Popped job was not the same as pushed"

    def _push(self, section):
        self.sections.append(section)

    def _pop(self, expetcted):
        popped = self.sections.pop()
        assert popped == expetcted, "Popped section was not same as pushed"

    def section(self, name):
        return Section(self, self.current_section, name)

    @property
    def current_section(self):
        return self.sections[-1]


class Section(object):
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

        self.sections = []

    def __enter__(self):
        self.job._push(self)

    def __exit__(self, _type, value, traceback):
        self.job._pop(self)


def with_new_section(func):
    @function_using_current_job
    @wraps(func)
    def decorated(job, *args, **kwargs):
        with job.section(utils.get_callable_name(func)):
            return func(*args, **kwargs)

    return decorated


def function_using_current_job(*attributes):
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
            injected_args = args[:1] + job_args + args[1:]
            return func(*injected_args, **kwargs)

        return decorated

    if utils.is_argumentless_decorator(attributes):
        func = attributes[0]
        attributes = tuple()
        return decorator(func)
    else:
        return decorator


def creating_new_job(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        with context.new_job():
            return func(*args, **kwargs)

    return decorated
