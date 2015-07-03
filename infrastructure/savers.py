# import utils


class BaseSaver(object):
    # @utils.not_implemented
    def __init__(self, *args, **kwargs):
        pass

    # @utils.not_implemented
    def save(self, data):
        pass

    # @utils.not_implemented
    def save_no_data(self):
        pass

    def __repr__(self):
        return self.__class__.__name__


class DbSaver(BaseSaver):
    pass


class PrintSaver(BaseSaver):
    def __init__(self, *args, **kwargs):
        pass

    def save(self, data):
        print 'Save with data'
        for datum in data:
            print datum

    def save_no_data(self):
        print 'Save with no data'
