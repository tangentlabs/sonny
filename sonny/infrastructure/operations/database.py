from abc import ABCMeta, abstractmethod, abstractproperty


class DatabaseAccess(object):
    """
    Helper to access the database, usually from the database information from
    DBRegistry
    """
    connectors_classes = {}

    @classmethod
    def register_connector(cls, connector_class):
        """
        Register a database connector, for a specific engine or database type
        """
        cls.connectors_classes[connector_class.connector_name] = connector_class

        return connector_class

    def create_connection(self, connector_name, *args, **kwargs):
        """
        Create a connection by passing the natural for database type arguments

        Mirrors the DatabaseConnector method
        """
        connector_class = self.connectors_classes[connector_name]
        connector = connector_class()
        connection = connector.create_connection(*args, **kwargs)

        return connection

    def create_connection_from_info(self, database):
        """
        Create a connection by passing a database info from DBRegistry

        Mirrors the DatabaseConnector method
        """
        connector_name = database['connector_name']
        connector_class = self.connectors_classes[connector_name]
        connector = connector_class()
        connection = connector.create_connection_from_info(database)

        return connection


class DatabaseConnector(object):
    """
    Database connector interface. It can create connections to a database
    """
    __metaclass__ = ABCMeta

    @abstractproperty
    def connector_name(self):
        """
        The unique identifier for this Connector
        """
        pass

    @abstractmethod
    def create_connection(self, *args, **kwargs):
        """
        Create a connection by passing the natural for database type arguments
        """
        pass

    @abstractmethod
    def create_connection_from_info(self, database):
        """
        Create a connection by passing a database info from DBRegistry
        """
        pass


@DatabaseAccess.register_connector
class MySqlDatabaseConnector(DatabaseAccess):
    """
    MySql connector class
    """
    connector_name = 'MySql'

    def create_connection(self, *args, **kwargs):
        import MySQLdb
        connection = MySQLdb.connect(*args, **kwargs)
        connection.set_character_set('utf8')

        return connection

    def create_connection_from_info(self, database):
        return self.create_connection(
            host=database['host'],
            port=database['port'],
            user=database['username'],
            passwd=database['password'],
            db=database['database'],
        )


@DatabaseAccess.register_connector
class PostgresDatabaseConnector(DatabaseAccess):
    """
    Postgres connector class
    """
    connector_name = 'Postgres'

    def create_connection(self, *args, **kwargs):
        import psycopg2
        connection = psycopg2.connect(*args, **kwargs)
        return connection

    def create_connection_from_info(self, database):
        return self.create_connection(
            host=database['host'],
            port=database['port'],
            user=database['username'],
            password=database['password'],
            database=database['database'],
        )


@DatabaseAccess.register_connector
class MsSqlDatabaseConnector(DatabaseAccess):
    """
    MsSql connector class
    """
    connector_name = 'Mssql'

    def create_connection(self, *args, **kwargs):
        import pymssql
        connection = pymssql.connect(*arg, **kwargs)
        return connection

    def create_connection_from_info(self, database):
        return self.create_connection(
            server=database['host'],
            port=database['port'],
            user=database['username'],
            password=database['password'],
            database=database['database'],
        )
