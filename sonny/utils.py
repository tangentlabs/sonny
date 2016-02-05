import os
import math
from importlib import import_module


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


CONF_ENV_VAR_NAME = "IMPORT_CONF"


def get_config_module(config_module_name=None):
    if config_module_name is None:
        config_module_name = os.environ.get(CONF_ENV_VAR_NAME, "conf.local")

    try:
        config = import_module(config_module_name)
    except ImportError, e:
        raise Exception("Could not load config module '%s'. Make sure "
                        "that you specified properly in env variable %s, "
                        "and that it can be loaded:\n %s"
                        % (config_module_name,
                           CONF_ENV_VAR_NAME, e))
    config.environment = getattr(config, 'environment', config_module_name)

    return config_module_name, config
