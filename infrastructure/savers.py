import MySQLdb

import utils
from mockable import Mockable


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

    def save(self, data):
        self.cursor.executemany(self.query, data)
        self.connection.commit()

    def save_no_data(self):
        self.save([])


class PrintSaver(BaseSaver):
    def __init__(self, *args, **kwargs):
        pass

    def save(self, data):
        print 'Save with data'
        for datum in data:
            print datum

    def save_no_data(self):
        print 'Save with no data'
