from abc import ABCMeta, abstractmethod

import MySQLdb

from infrastructure import context

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
    @context.method_using_current_job("db_registry")
    def __init__(self, db_registry, destination):
        self.db_registry = db_registry
        self.destination = destination
        with open(destination['file'], 'rb') as _file:
            self.query = _file.read()

        database = self.db_registry["databases"][self.destination["database"]]
        host = db_registry["hosts"][database["host"]]
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

    @context.job_step_method
    def save(self, data):
        self.cursor.executemany(self.query, data)
        self.connection.commit()

    @context.job_step_method
    def save_no_data(self):
        self.save([])


@BaseSaver.register_default_noop
class PrintSaver(BaseSaver):
    def __init__(self, *args, **kwargs):
        pass

    @context.job_step_method
    def save(self, data):
        print 'Save with data'
        for datum in data:
            print datum

    @context.job_step_method
    def save_no_data(self):
        print 'Save with no data'
