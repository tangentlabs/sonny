from infrastructure.facilities.generic_config_registry import GenericConfigRegistry

from infrastructure.context import helpers


@helpers.register_facility("email_registry")
class EmailRegistry(GenericConfigRegistry):
    registry_config_name = "email_registry"
