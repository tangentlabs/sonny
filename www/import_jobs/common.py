from abc import ABCMeta, abstractmethod, abstractproperty

from infrastructure.context import helpers

from infrastructure.facilities import everything  # noqa

from import_jobs.base import Importer

from infrastructure.operations import fetchers
from infrastructure.operations import loaders
from infrastructure.operations import transformers
from infrastructure.operations import formatters
from infrastructure.operations import savers
from infrastructure.operations import file_deleters
import re


class FtpDbImporter(Importer):
    """
    An abstract ftp->db importer:
    * Use FTP for importing
    * Use a DB for inserting
    * Use a local file deleter
    """
    __metaclass__ = ABCMeta

    fetcher = fetchers.FtpFetcher
    saver = savers.DbSaver
    deleter = file_deleters.LocalFileDeleter

    def __init__(self, files_to_fetch=None, **kwargs):
        super(FtpDbImporter, self).__init__(
            files_to_fetch=files_to_fetch, **kwargs)

    @abstractproperty
    def loader(self):
        pass

    @abstractproperty
    def file_regex(self):
        pass

    @abstractproperty
    def ftp_server(self):
        pass

    @helpers.step
    def do_run(self):
        with fetchers.LocalFileContextManager(
                self.get_files_list(),
                self.fetcher(self.ftp_server),
                self.deleter()) as local_filenames:
            if not local_filenames:
                return

            self.pre_insert()
            for local_filename, exception in local_filenames:
                data = self.loader().get_all_data_with_headers(local_filename)
                data = self.transform_data(data)
                self.saver(self.insert_queries).save(data)
            self.post_insert()

    @helpers.step
    def pre_insert(self):
        for pre_insert_query in self.pre_insert_queries:
            self.saver(pre_insert_query).save_no_data()

    @helpers.step
    def post_insert(self):
        for post_insert_query in self.post_insert_queries:
            self.saver(post_insert_query).save_no_data()

    @helpers.step
    def transform_data(self, data):
        return data

    def get_files_list(self):
        return [self.get_latest_file()]

    def version_from_filename(self, filename):
        version = re.match(self.file_regex, filename).groups()[1]
        return float(version)

    def get_files_to_fetch(self):
        fetcher = self.fetcher(self.ftp_server)
        all_remote_filenames = fetcher.search_regex_files('', self.file_regex)
        filenames = sorted(all_remote_filenames, key=self.version_from_filename, reverse=True)
        return filenames

    def get_latest_file(self):
        filenames = self.files_to_fetch
        return filenames[0]


class FtpCsvDbImporter(FtpDbImporter):
    loader = loaders.CsvLoader


class FtpExcelDbImporter(FtpDbImporter):
    loader = loaders.ExcelLoader


class EmailLoadTransformInsertDeleteImporter(Importer):
    """
    * Fetch today's files from email using config search params
    * Load them
    * Transform them
    * Insert them, potentionally in multiple queries
    * Delete the files
    """

    @abstractproperty # noqa
    def email_source(self): pass # noqa
    file_pattern = '*.xls*'
    @abstractproperty # noqa
    def insert_queries(self): pass # noqa

    fetcher = fetchers.EmailFetcher
    _loader = loaders.ExcelLoader
    saver = savers.DbSaver
    file_deleter = file_deleters.LocalFileDeleter

    @helpers.step
    def do_run(self):
        search_kwargs = self.get_search_kwargs()
        local_filenames = self.fetcher(self.email_source, self.file_pattern)\
            .fetch_from_search('INBOX', **search_kwargs)

        try:
            for local_filename in local_filenames:
                data = self._loader().get_all_data_with_headers(local_filename)
                data = self.transform_data(data)

                if len(self.insert_queries) > 1:
                    # TODO: Perhaps we should be loading the file twice,
                    # instead of creating a potentionally big tuple in-memory?
                    data = transformers.generator_to_tuples()(data)

                for insert_query in self.insert_queries:
                    self.saver(insert_query).save(data)
        finally:
            self.file_deleter().delete_files(local_filenames)

    def get_files_to_fetch(self):
        return None

    @helpers.step
    def get_search_kwargs(self):
        if self.files_to_fetch is not None:
            return {
                'filenames': self.files_to_fetch,
            }
        else:
            kwargs = self.get_email_search_kwargs()
            kwargs.update({
                'Date__contains': formatters.date_format.imap(self._today),
            })

            return kwargs

    def get_email_search_kwargs(self):
        return self.job.job_config['email_search_query']

    @helpers.step
    def transform_data(self, data):
        return data
