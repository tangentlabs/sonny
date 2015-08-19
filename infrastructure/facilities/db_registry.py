from infrastructure.facilities.generic_config_registry import GenericConfigRegistry

from infrastructure.context import helpers


@helpers.register_facility("db_registry")
class DbRegistry(GenericConfigRegistry):
    registry_config_name = "db_registry"

    def get_database(self, alias):
        """
        Get all the database info for a database alias
        """
        database = self["databases"][alias]
        host = self["hosts"][database["host"]]
        user = host["users"][database["user"]]
        db = host["databases"][database["database"]]
        return {
            "host": host['host'],
            "port": int(host['port']),
            "user": user['username'],
            "password": user['password'],
            "database": db,
        }
