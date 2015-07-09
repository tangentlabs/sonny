from infrastructure.facilities.generic_config_registry import GenericConfigRegistry

from infrastructure.context import context


@context.register_job_facility_factory("db_registry")
class DbRegistry(GenericConfigRegistry):
    registry_config_name = "db_registry"
