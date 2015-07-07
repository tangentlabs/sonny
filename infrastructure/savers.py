import MySQLdb

import utils
from mockable import Mockable
import context


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
    def __init__(self, db_registry, destination):
        self.db_registry = db_registry
        self.destination = destination
        with open(destination['file'], 'rb') as _file:
            self.query = _file.read()

        host = db_registry["hosts"][destination["host"]]
        user = host["users"][destination["user"]]
        db = host["databases"][destination["db"]]
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
