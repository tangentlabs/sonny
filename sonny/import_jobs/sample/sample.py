from datetime import date

from sonny import utils

from sonny.import_jobs import common
from sonny.infrastructure.facilities.job_config import JobConfig

location = utils.make_location(__file__)


class SampleImporter(common.FtpCsvDbImporter):
    """
    Sample Importer
    New customers for today
    """
    class JobSettings(common.FtpCsvDbImporter.JobSettings):
        class JobConfigFacilitySettings(JobConfig.FacilitySettings):
            filename = location("sample.yaml")

        test_defaults = {
            "files_to_fetch": [location("sample.csv")],
        }

    uuid = '6e26c903-a4ca-4216-93b9-872765c6c888'

    ftp_server = "main"

    @property
    def file_regex(self):
        return r'(.*)NEW_Accounts_\.(.*)\.csv'

    pre_insert_queries = []

    insert_queries = {
        "database": "dashboard",
        "file": location("sample.sql"),
    }

    post_insert_queries = [
        {
            "database": "dashboard",
            "file": location("sample_post.sql"),
        }
    ]
