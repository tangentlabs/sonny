from datetime import date

import utils

from infrastructure.facilities import logging, profiling  # noqa

from import_jobs import common

location = utils.make_location(__file__)


class SampleImporter(common.FtpCsvDbImporter):
    """
    Sample Importer
    New customers for today
    """

    ftp_server = "main"

    insert_query_fields = [
        "Account Number",
        "Customer Name",
        "Address 1",
        "Address 2",
        "Address 3",
        "Address 4",
        "Telephone",
        "Opened",
    ]

    insert_query = {
        "database": "dashboard_live",
        "file": location("sample.sql"),
    }
    post_job_query = {
        "database": "dashboard_live",
        "file": location("sample_post.sql"),
    }

    test_files_to_fetch = [location("sample.csv")]

    def get_ftp_files_to_fetch(self):
        return ['NEW_Accounts_%s.csv' % date.today().strftime('%d%m%Y')]


if __name__ == '__main__':
    SampleImporter.from_command_line()
