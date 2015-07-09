from infrastructure.facilities.generic_config_registry import GenericConfigRegistry

from infrastructure.context import context


@context.register_job_facility_factory("email_registry")
class EmailRegistry(GenericConfigRegistry):
    registry_config_name = "email_registry"
