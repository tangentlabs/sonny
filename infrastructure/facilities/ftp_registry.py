from infrastructure.facilities.generic_config_registry import GenericConfigRegistry

from infrastructure.context import helpers


@helpers.register_job_facility_factory("ftp_registry")
class FtpRegistry(GenericConfigRegistry):
    registry_config_name = "ftp_registry"
