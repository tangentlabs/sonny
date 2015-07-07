import utils

from infrastructure import context

from infrastructure.transformers import dicts_to_tuples
from infrastructure.fetchers import FtpFetcher
from infrastructure.loaders import CsvLoader
from infrastructure.savers import DbSaver
from infrastructure.file_deleters import LocalFileDeleter


class BaseImporter(object):
    """
    A basic interface for importers
    """

    @classmethod
    @context.creating_new_job
    def create_and_run(cls, *args, **kwargs):
        importer = cls(*args, **kwargs)
        importer.run_import()

    @context.auto_method_section
    @utils.not_implemented
    def run_import(self):
        pass


class FetchLoadInsertDeleteCleanupImporter(object):
    """
    As the name describes:
    * Fetch a file
    * Load it
    * Insert it into a data store
    * Delete the fetched files
    * Run a post-job script
    """
    ftp_registry = None
    db_registry = None

    files_source = None
    insert_query_fields = None
    insert_query = None
    post_job_query = None

    fetcher = None
    _loader = None
    saver = None
    deleter = None

    @context.auto_method_section
    def run_import(self):
        filenames = self.get_filenames()
        local_filenames = self.fetcher(self.ftp_registry, self.files_source).fetch_files(filenames)
        for local_filename in local_filenames:
            data = self._loader().get_all_data(local_filename)
            data = dicts_to_tuples(self.insert_query_fields)(data)
            self.saver(self.db_registry, self.insert_query).save(data)
        self.deleter().delete_files(local_filenames)
        self.saver(self.db_registry, self.post_job_query).save_no_data()

    @context.auto_method_section
    @utils.not_implemented
    def get_filenames(self):
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
