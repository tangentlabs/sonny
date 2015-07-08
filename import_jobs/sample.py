from datetime import date

import utils

from infrastructure.facilities import logging, profiling  # noqa

from infrastructure.operations import importers

location = utils.make_location(__file__)


class SampleImporter(importers.FtpCsvDbImporter):
    """
    Sample Importer
    Import NRR Plumb WDL New customers for today
    """

    ftp_server = "toolkit"

    insert_query_fields = [
        "ACCNO",
        "STBR",
        "CUSTOMER",
        "LIMIT",
        "ADDRESS01",
        "ADDRESS02",
        "ADDRESS03",
        "ADDRESS04",
        "ADDRESS05",
        "TELEPHONE",
        "TERMS",
        "OPENED",
    ]

    insert_query = {
        "database": "dashboard_live",
        "file": location("sample.sql"),
    }
    post_job_query = {
        "database": "dashboard_live",
        "file": location("sample_post.sql"),
    }

    def ftp_files_to_fetch(self):
        return ['NEW_Accounts_%s.csv' % date.today().strftime('%d%m%Y')]


if __name__ == '__main__':
    SampleImporter.run()
