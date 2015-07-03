import utils


class BaseSaver(object):
    # @utils.not_implemented
    def __init__(self, *args, **kwargs):
        pass

    # @utils.not_implemented
    @utils.log_call
    def save(self, data):
        pass

    # @utils.not_implemented
    @utils.log_call
    def save_no_data(self):
        pass

    def __repr__(self):
        return self.__class__.__name__


class DbSaver(BaseSaver):
    pass
