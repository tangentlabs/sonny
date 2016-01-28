from tangent_importer.infrastructure.facilities.generic_config_registry import GenericConfigRegistry

from tangent_importer.infrastructure.context import helpers


@helpers.register_facility("ftp_registry")
class FtpRegistry(GenericConfigRegistry):
    registry_config_name = "ftp_registry"

    def get_ftp_server(self, alias):
        """
        Get all the FTP server info for an FTP server alias
        """
        return self[alias]
