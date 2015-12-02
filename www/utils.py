import os
import math


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


def pretty_bytes(_bytes):
    """Render bytes with an appropriate size"""

    suffixes = ["", "K", "M", "G", "P"]
    if _bytes == 0:
        scale = 0
    else:
        scale = int(math.floor(math.log(_bytes, 1024)))
    if scale >= len(suffixes):
        scale = len(suffixes) - 1

    suffix = suffixes[scale]
    scaled_bytes = _bytes / (1024 ** scale)

    return "%s%sb" % (scaled_bytes, suffix)
