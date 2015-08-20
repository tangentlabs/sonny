from abc import abstractmethod

import MySQLdb

from infrastructure.context import helpers

from infrastructure.operations.base import BaseOperation


class NoDBRowMatched(Exception):
    pass


class BaseDbLoader(BaseOperation):
    class OperationSettings(BaseOperation.OperationSettings):
        __job_settings_name__ = 'DbLoaderOperationSettings'
        cached = {}

    @abstractmethod
    def get_single(self, parameters):
        pass

    @abstractmethod
    def get_multiple(self, parameters):
        pass


@BaseDbLoader.auto_mock_for_local_testing
class DbLoader(BaseDbLoader):
    def __init__(self, source):
        super(DbLoader, self).__init__()

        job = helpers.get_current_job()
        self.db_registry = job.db_registry
        self.source = source
        with open(source['file'], 'rb') as _file:
            self.query = _file.read()

        database = self.db_registry.get_database(self.source["database"])
        self.connection = MySQLdb.connect(
            host=database['host'],
            port=database['port'],
            user=database['user'],
            passwd=database['password'],
            db=database['database'],
        )
        self.cursor = self.connection.cursor()

    def _get_column_names(self):
        return tuple(
            name
            for name, _, _, _, _, _, _
            in self.cursor.description
        )

    def _as_dict(self, column_names, row):
        return dict(zip(column_names, row))

    @helpers.step
    def get_single(self, parameters):
        self.cursor.execute(self.query, parameters)
        column_names = self._get_column_names()
        row = self.cursor.fetchone()
        if row is None:
            raise NoDBRowMatched()
        return self._as_dict(column_names, row)

    @helpers.step
    def get_multiple(self, parameters):
        self.cursor.execute(self.query, parameters)
        column_names = self._get_column_names()
        for row in self.cursor.fetchall():
            yield self._as_dict(column_names, row)


@BaseDbLoader.register_default_noop
class CachedDbLoader(BaseDbLoader):
    def __init__(self, source):
        super(CachedDbLoader, self).__init__()

        self.source = source
        self.cached = self._get_cached_queries(self.source)

    def _get_cached_queries(self, source):
        cached = self.OperationSettings.cached[source['database']]
        for filename, queries in cached.iteritems():
            if source['file'].endswith(filename):
                return queries

    def _get_cached_query(self, parameters):
        if isinstance(parameters, dict):
            parameters = tuple(sorted(parameters.iteritems()))
        elif isinstance(parameters, list):
            parameters = tuple(list)
        return self.cached[parameters]

    @helpers.step
    def get_single(self, parameters):
        return self._get_cached_query(parameters)

    @helpers.step
    def get_multiple(self, parameters):
        row = self._get_cached_query(parameters)
        if row is None:
            raise NoDBRowMatched()
        return row
