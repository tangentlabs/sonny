import os
from functools import wraps


def make_location(_file_):
    """
    Create a location function, as used in Django, that returns a filename
    relative the the __file__ provided as argument
    """
    def location(*paths):
        realpath = os.path.realpath(_file_)
        dirname = os.path.dirname(realpath)
        joined = os.path.join(dirname, *paths)

        return joined

    return location


def is_callable(potentional_callable):
    return hasattr(potentional_callable, '__call__')


def is_method(func):
    return hasattr(func, 'im_class')


def get_method_name(method):
    return '%s.%s' % (method.im_class.__name__, method.im_func.func_name)


def get_function_name(func):
    return func.func_name


def get_callable_name(func):
    if is_method(func):
        return get_method_name(func)
    else:
        return get_function_name(func)


def is_method_or_class_method(func):
    """
    Decide if a function is a method or class method, by looking at the
    method attributes, and the variable names
    """
    if hasattr(func, 'im_func'):
        return True

    # 'self_or_cls' is used by some helper functions, that don't know if they
    # methods or class methods, but want to use the self/cls argument anyway
    return hasattr(func, 'func_code') \
        and func.func_code.co_argcount >= 1 \
        and func.func_code.co_varnames[0] in ('self', 'cls', 'self_or_cls')


def is_argumentless_decorator(decorator_args):
    """
    Find out if a decorator is used as a function decorator with no arguments

    @decorator
    def f()
        pass

    Or if it is used as decorator with parameters

    @decorator("a", b)
    def g()
        pass
    """
    if len(decorator_args) != 1:
        return False

    potentional_callable = decorator_args[0]
    return is_callable(potentional_callable)


def combine_context_managers(*context_managers):
    """
    Combine context managers into a new one, so that they enter and exit in the
    right order, even if there is a error in the enter or exit of one of them
    """
    class CombinedContextManager(object):
        def __init__(self, first, second):
            self.first = first
            self.second = second

        def __enter__(self):
            """
            Ensure that the first one exits if the second one fails to enter
            """
            result = self.first.__enter__()
            try:
                self.second.__enter__()
            except Exception as exc:
                self.first.__exit__(type(exc), exc, None)
                raise

            return result

        def __exit__(self, _type, value, traceback):
            """
            Ensure the first one exits even if the second one fails to exit
            """
            try:
                self.second.__exit__(_type, value, traceback)
            finally:
                self.first.__exit__(_type, value, traceback)

    combined = context_managers[0]
    for _next in context_managers[1:]:
        combined = CombinedContextManager(combined, _next)

    return combined
