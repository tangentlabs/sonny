import MySQLdb

import utils
from mockable import Mockable
from context import with_new_section
from logging import log_method_call
from profiling import profile_method


class BaseSaver(Mockable):
    @utils.not_implemented
    def __init__(self, *args, **kwargs):
        pass

    @utils.not_implemented
    def save(self, data):
        pass

    @utils.not_implemented
    def save_no_data(self):
        pass

    def __repr__(self):
        return self.__class__.__name__


class DbSaver(BaseSaver):
    def __init__(self, destination):
        self.destination = destination
        with open(destination['file'], 'rb') as _file:
            self.query = _file.read()
        self.connection = MySQLdb.connect(
            host=destination['host'],
            user=destination['username'],
            passwd=destination['password'],
            db=destination['db'],
            port=int(destination['port']))
        self.cursor = self.connection.cursor()

    @with_new_section
    @profile_method
    @log_method_call
    def save(self, data):
        self.cursor.executemany(self.query, data)
        self.connection.commit()

    @with_new_section
    @profile_method
    @log_method_call
    def save_no_data(self):
        self.save([])


@BaseSaver.register_default_noop
class PrintSaver(BaseSaver):
    def __init__(self, *args, **kwargs):
        pass

    @with_new_section
    @profile_method
    @log_method_call
    def save(self, data):
        print 'Save with data'
        for datum in data:
            print datum

    @with_new_section
    @profile_method
    @log_method_call
    def save_no_data(self):
        print 'Save with no data'
