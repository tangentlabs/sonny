from abc import abstractmethod

import MySQLdb

from tangent_importer.infrastructure.context import helpers
from tangent_importer.infrastructure.operations.base import BaseOperation
from tangent_importer.infrastructure.operations.utils import batch


class BaseSaver(BaseOperation):
    @abstractmethod
    def save(self, data):
        pass

    @abstractmethod
    def save_no_data(self):
        pass

    @abstractmethod
    def save_no_data_multiple_queries(self):
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
        self.multiple_queries = self._split_multiple_queries()

        database = self.db_registry.get_database(self.destination["database"])
        self.connection = MySQLdb.connect(
            host=database['host'],
            port=database['port'],
            user=database['username'],
            passwd=database['password'],
            db=database['database'],
        )
        self.cursor = self.connection.cursor()

    def _split_multiple_queries(self):
        """
        A bit primitive way to split mutliple queries in a string, as MySQLdb
        doesn't allow running multiple queries in one call.

        Each query needs to end with a semicolon and a newline, and this is
        optional for the last query
        """
        return filter(None, map(str.strip, self.query.split(';\n')))

    @helpers.step
    def save(self, data):
        for batched_rows in batch(data):
            self.cursor.executemany(self.query, batched_rows)
        self.connection.commit()

    @helpers.step
    def save_no_data(self):
        self.save([[]])

    @helpers.step
    def save_no_data_multiple_queries(self):
        for query in self.multiple_queries:
            self.cursor.execute(query, [])
        self.connection.commit()


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

    @helpers.step
    def save_no_data_multiple_queries(self):
        print 'save_no_data_multiple_queries'
