from functools import wraps

import utils


class Context(object):
    def __init__(self):
        self.job_stack = []
        self.job_attribute_factories = {}

    def new_job(self):
        job = Job(self)

        for attribute_name, attribute_factory in \
                self.job_attribute_factories.iteritems():
            attribute = attribute_factory()
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


# Global context
context = Context()


class Job(object):
    def __init__(self, context):
        self.context = context

    def __enter__(self):
        self.context._push(self)

        return self

    def __exit__(self, _type, value, traceback):
        popped = self.context._pop()
        assert popped == self, "Popped job was not the same as pushed"


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
