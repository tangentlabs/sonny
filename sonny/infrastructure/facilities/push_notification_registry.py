from sonny.infrastructure.facilities.generic_config_registry import GenericConfigRegistry

from sonny.infrastructure.context import helpers


@helpers.register_facility("push_notification_registry")
class PushNotificationRegistry(GenericConfigRegistry):
    registry_config_name = "push_notification_registry"

    def get_push_notification_config(self, alias):
        """
        Get all the FTP server info for an FTP server alias
        """
        return self[alias]
