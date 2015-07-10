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
