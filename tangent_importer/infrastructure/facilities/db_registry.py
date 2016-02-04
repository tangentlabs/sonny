import MySQLdb

from tangent_importer.infrastructure.facilities.generic_config_registry import GenericConfigRegistry

from tangent_importer.infrastructure.context import helpers


@helpers.register_facility("db_registry")
class DbRegistry(GenericConfigRegistry):
    registry_config_name = "db_registry"

    def get_database(self, alias):
        """
        Get all the database info for a database alias
        """
        return self[alias]

    def create_connection_to_database(self, alias):
        """
        Helper function to create a connection to a database by alias
        """
        database = self.get_database(alias)
        return self.create_connection_to_database_from_info(database)

    @classmethod
    def create_connection_to_database_from_info(cls, database):
        connection = MySQLdb.connect(
            host=database['host'],
            port=database['port'],
            user=database['username'],
            passwd=database['password'],
            db=database['database'],
        )

        return connection
