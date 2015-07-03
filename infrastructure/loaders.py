# import utils


class BaseLoader(object):
    # @utils.not_implemented
    def __init__(self, *args, **kwargs):
        pass

    # @utils.not_implemented
    def get_all_data(self, filename):
        return [{}]

    def __repr__(self):
        return self.__class__.__name__


class CsvLoader(BaseLoader):
    pass
