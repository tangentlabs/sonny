from datetime import date

from tangent_importer import utils

from tangent_importer.import_jobs import common

location = utils.make_location(__file__)


class SampleImporter(common.FtpCsvDbImporter):
    """
    Sample Importer
    Import NRR Plumb WDL New customers for today
    """

    uuid = '6e26c903-a4ca-4216-93b9-872765c6c888'

    ftp_server = "toolkit"

    insert_query = {
        "database": "dashboard_live",
        "file": location("sample.sql"),
    }
    post_job_query = {
        "database": "dashboard_live",
        "file": location("sample_post.sql"),
    }

    test_defaults = {
        "ftp_files_to_fetch": [location("sample.csv")],
    }

    def get_ftp_files_or_search_to_fetch(self):
        is_pattern = False
        filenames = ['NEW_Accounts_%s.csv' % date.today().strftime('%d%m%Y')]
        return filenames, is_pattern
