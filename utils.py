import os


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


def get_callable_name(func):
    if hasattr(func, 'func_name'):
        return func.func_name

    if hasattr(func, 'im_func'):
        return func.im_func.func_name

    if hasattr(func, '__name__'):
        return func.__name__

    return None
