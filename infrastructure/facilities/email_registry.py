from infrastructure.facilities.generic_config_registry import GenericConfigRegistry

from infrastructure.context import helpers


@helpers.register_facility("email_registry")
class EmailRegistry(GenericConfigRegistry):
    registry_config_name = "email_registry"

    def get_email_server(self, alias):
        """
        Get all the email server info for an email server alias
        """
        return self[alias]
