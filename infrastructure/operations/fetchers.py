from ftplib import FTP
import tempfile

import utils

from infrastructure import context

from infrastructure.facilities.mockable import Mockable


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
    def __init__(self, ftp_registry, source):
        self.ftp_registry = ftp_registry
        self.source = source
        self.ftp = None

    def __enter__(self):
        host = self.ftp_registry["hosts"][self.source["host"]]
        user = host["users"][self.source["user"]]
        self.ftp = FTP(host["server"])
        self.ftp.login(user['username'], user['password'])

        return self.ftp

    def __exit__(self, _type, value, traceback):
        self.ftp.close()
        self.ftp = None


class FtpFetcher(BaseFileFetcher):
    def __init__(self, ftp_registry, source):
        self.ftp_registry = ftp_registry
        self.source = source

    @context.job_step_method
    def fetch_file(self, filename):
        with FtpContextManager(self.ftp_registry, self.source) as ftp:
            _, local_filename = tempfile.mkstemp()
            with open(local_filename, 'wb') as local_file:
                ftp.retrbinary('RETR %s' % filename, local_file.write)

        return local_filename


@BaseFileFetcher.register_default_noop
class NoOpFetcher(BaseFileFetcher):
    def __init__(self, *args, **kwargs):
        pass

    @context.job_step_method
    def fetch_file(self, filename):
        return filename
