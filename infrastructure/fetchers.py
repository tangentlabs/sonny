# import utils


class BaseFileFetcher(object):
    # @utils.not_implemented
    def __init__(self, *args, **kwargs):
        pass

    # @utils.not_implemented
    def fetch_files(self, filenames):
        return filenames

    def __repr__(self):
        return self.__class__.__name__


class FtpFetcher(BaseFileFetcher):
    pass
