import utils

from infrastructure import context

from infrastructure.operations.transformers import dicts_to_tuples
from infrastructure.operations.fetchers import FtpFetcher
from infrastructure.operations.loaders import CsvLoader
from infrastructure.operations.savers import DbSaver
from infrastructure.operations.file_deleters import LocalFileDeleter


class BaseImporter(object):
    """
    A basic interface for importers
    """
    ftp_registry = {
        "hosts": {
            "main_host": {
                "server": "upload.tangentuk.com",
                "users": {
                    "main_user": {
                        "username": "newaccounts_plumbcenter",
                        "password": "CdVdPte8",
                    },
                },
            },
        },
        "servers": {
            "toolkit": {
                "host": "main_host",
                "user": "main_user",
            }
        }
    }
    db_registry = {
        "hosts": {
            "main_host": {
                "host": "127.0.0.1",
                "port": "3306",
                "users": {
                    "main_user": {
                        "username": "app-dash-dev",
                        "password": "app-dash-dev",
                    }
                },
                "databases": {
                    "main_database": "miniTao_Wolseley",
                },
            },
        },
        "databases": {
            "dashboard_live": {
                "host": "main_host",
                "user": "main_user",
                "database": "main_database",
            }
        }
    }

    @classmethod
    @context.create_for_job
    def run(cls, *args, **kwargs):
        importer = cls(*args, **kwargs)
        importer.run_import()

    @utils.must_be_implemented_by_subclasses
    def run_import(self):
        pass


class FetchLoadInsertDeleteCleanupImporter(BaseImporter):
    """
    As the name describes:
    * Fetch a file
    * Load it
    * Insert it into a data store
    * Delete the fetched files
    * Run a post-job script
    """
    file_server = None
    insert_query_fields = None
    insert_query = None
    post_job_query = None

    fetcher = None
    _loader = None
    saver = None
    deleter = None

    @context.job_step_method
    def run_import(self):
        filenames = self.files_to_fetch()
        local_filenames = self.fetcher(self.ftp_registry, self.file_server).fetch_files(filenames)
        for local_filename in local_filenames:
            data = self._loader().get_all_data(local_filename)
            data = dicts_to_tuples(self.insert_query_fields)(data)
            self.saver(self.db_registry, self.insert_query).save(data)
        self.deleter().delete_files(local_filenames)
        self.saver(self.db_registry, self.post_job_query).save_no_data()

    @context.job_step_method
    @utils.must_be_implemented_by_subclasses
    def files_to_fetch(self):
        """The filenames to fetch from the remote location"""
        pass


class FtpCsvDbImporter(FetchLoadInsertDeleteCleanupImporter):
    """
    A more specific improter:
    * Use FTP for importing
    * Use CSV for loading
    * Use a DB for inserting
    * Use a local file deleter
    """
    fetcher = FtpFetcher
    _loader = CsvLoader
    saver = DbSaver
    deleter = LocalFileDeleter

    @context.job_step_method
    def files_to_fetch(self):
        return self.ftp_files_to_fetch()

    @utils.must_be_implemented_by_subclasses
    def ftp_files_to_fetch(self):
        pass

    @property
    def file_server(self):
        return self.ftp_server
