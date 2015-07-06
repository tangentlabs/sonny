import tempfile
from ftplib import FTP

import utils
from mockable import Mockable
from logging import log_method_call
from profiling import profile_method


class BaseFileFetcher(Mockable):
    @utils.not_implemented
    def __init__(self, *args, **kwargs):
        pass

    @utils.not_implemented
    def fetch_file(self, filename):
        return filename

    def fetch_files(self, filenames):
        return [
            self.fetch_file(filename)
            for filename in filenames
        ]

    def __repr__(self):
        return self.__class__.__name__


class FtpContextManager(object):
    def __init__(self, source):
        self.source = source
        self.ftp = None

    def __enter__(self):
        self.ftp = FTP(self.source['server'])
        self.ftp.login(self.source['username'], self.source['password'])

        return self.ftp

    def __exit__(self, _type, value, traceback):
        self.ftp.close()
        self.ftp = None


class FtpFetcher(BaseFileFetcher):
    def __init__(self, source):
        self.source = source

    @profile_method
    @log_method_call
    def fetch_file(self, filename):
        with FtpContextManager(self.source) as ftp:
            _, local_filename = tempfile.mkstemp()
            with open(local_filename, 'wb') as local_file:
                ftp.retrbinary('RETR %s' % filename, local_file.write)

        return local_filename


@BaseFileFetcher.register_default_noop
class NoOpFetcher(BaseFileFetcher):
    def __init__(self, source):
        pass

    @profile_method
    @log_method_call
    def fetch_file(self, filename):
        return filename
