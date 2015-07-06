import utils

from infrastructure import context

from infrastructure.transformers import dicts_to_tuples
from infrastructure.fetchers import FtpFetcher
from infrastructure.loaders import CsvLoader
from infrastructure.savers import DbSaver
from infrastructure.file_deleters import LocalFileDeleter


class FtpCsvDbImporter(object):
    ftp_registry = None
    db_registry = None

    files_source = None
    insert_query_fields = None
    insert_query = None
    post_job_query = None

    @classmethod
    @context.creating_new_job
    def create_and_run(cls):
        importer = cls()
        importer.run_import()

    @context.auto_method_section
    def run_import(self):
        filenames = self.get_filenames()
        local_filenames = FtpFetcher(self.ftp_registry, self.files_source).fetch_files(filenames)
        for local_filename in local_filenames:
            data = CsvLoader().get_all_data(local_filename)
            data = dicts_to_tuples(self.insert_query_fields)(data)
            DbSaver(self.db_registry, self.insert_query).save(data)
        LocalFileDeleter().delete_files(local_filenames)
        DbSaver(self.db_registry, self.post_job_query).save_no_data()

    @utils.not_implemented
    @context.auto_method_section
    def get_filenames(self):
        pass
