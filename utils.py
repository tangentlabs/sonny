import os
from functools import wraps


def make_location(_file_):
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
    if len(decorator_args) != 1:
        return False

    potentional_callable = decorator_args[0]
    return is_callable(potentional_callable)


def not_implemented(method):
    @wraps(method)
    def decorated(*args, **kwargs):
        raise NotImplementedError(get_callable_name(method))

    return decorated
