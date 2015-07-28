from abc import ABCMeta

class BaseFacility(object):
    """
    A common interface for all facilities
    """
    __metaclass__ = ABCMeta

    def __init__(self, job):
        pass

    def __enter__(self):
        pass

    def __exit__(self, _type, value, traceback):
        pass

