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