from abc import ABCMeta, abstractmethod

import MySQLdb

from infrastructure.context import helpers

from infrastructure.facilities.mocking import Mockable


class BaseSaver(Mockable):
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, *args, **kwargs):
        pass

    @abstractmethod
    def save(self, data):
        pass

    @abstractmethod
    def save_no_data(self):
        pass

    def __repr__(self):
        return self.__class__.__name__


@BaseSaver.auto_mock_for_local_testing
class DbSaver(BaseSaver):
    def __init__(self, destination):
        job = helpers.get_current_job()
        self.db_registry = job.db_registry
        self.destination = destination
        with open(destination['file'], 'rb') as _file:
            self.query = _file.read()

        database = self.db_registry["databases"][self.destination["database"]]
        host = self.db_registry["hosts"][database["host"]]
        user = host["users"][database["user"]]
        db = host["databases"][database["database"]]
        self.connection = MySQLdb.connect(
            host=host['host'],
            port=int(host['port']),
            user=user['username'],
            passwd=user['password'],
            db=db,
        )
        self.cursor = self.connection.cursor()

    @helpers.step
    def save(self, data):
        self.cursor.executemany(self.query, data)
        self.connection.commit()

    @helpers.step
    def save_no_data(self):
        self.save([])


@BaseSaver.register_default_noop
class PrintSaver(BaseSaver):
    def __init__(self, *args, **kwargs):
        pass

    @helpers.step
    def save(self, data):
        print 'Save with data'
        for datum in data:
            print datum

    @helpers.step
    def save_no_data(self):
        print 'Save with no data'
