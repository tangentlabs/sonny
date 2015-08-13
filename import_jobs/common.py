from abc import abstractmethod, abstractproperty

from infrastructure.context import helpers

from infrastructure.facilities import everything  # noqa

from import_jobs.base import Importer

from infrastructure.operations import fetchers
from infrastructure.operations import loaders
from infrastructure.operations import transformers
from infrastructure.operations import formatters
from infrastructure.operations import savers
from infrastructure.operations import file_deleters


class FetchLoadInsertDeleteCleanupImporter(Importer):
    """
    As the name describes:
    * Fetch a file
    * Load it
    * Insert it into a data store
    * Delete the fetched files
    * Run a post-job script
    """
    @abstractproperty # noqa
    def file_server(self): pass # noqa
    @abstractproperty # noqa
    def insert_query(self): pass # noqa
    def post_job_query(self): pass # noqa

    @abstractproperty # noqa
    def fetcher(self): pass # noqa
    @abstractproperty # noqa
    def _loader(self): pass # noqa
    @abstractproperty # noqa
    def saver(self): pass # noqa
    @abstractproperty # noqa
    def deleter(self): pass # noqa

    @helpers.step
    def do_run(self):
        filenames_or_search_kwargs, is_pattern = self.files_or_search_to_fetch
        if is_pattern:
            search_kwargs = filenames_or_search_kwargs
            local_filenames = self.fetcher(self.file_server).fetch_files_from_search(**search_kwargs)
        else:
            filenames = filenames_or_search_kwargs
            local_filenames = self.fetcher(self.file_server).fetch_files(filenames)

        try:
            for local_filename in local_filenames:
                data = self._loader().get_all_data_with_headers(local_filename)
                data = self.transform_data(data)
                self.saver(self.insert_query).save(data)
        finally:
            self.deleter().delete_files(local_filenames)
        self.saver(self.post_job_query).save_no_data()

    @helpers.step
    def transform_data(self, data):
        return data

    @property
    def files_or_search_to_fetch(self):
        if self.files_to_fetch:
            is_pattern = False
            filenames = self.files_to_fetch
        else:
            filenames, is_pattern = self.get_files_or_search_to_fetch()

        return filenames, is_pattern

    @helpers.step
    @abstractmethod
    def get_files_or_search_to_fetch(self):
        """
        The filenames, or search pattern, to fetch from the remote location
        """
        pass


class FtpCsvDbImporter(FetchLoadInsertDeleteCleanupImporter):
    """
    A more specific importer:
    * Use FTP for importing
    * Use CSV for loading
    * Use a DB for inserting
    * Use a local file deleter
    """
    fetcher = fetchers.FtpFetcher
    _loader = loaders.CsvLoader
    saver = savers.DbSaver
    deleter = file_deleters.LocalFileDeleter

    def __init__(self, ftp_files_to_fetch=None, **kwargs):
        super(FtpCsvDbImporter, self).__init__(
            files_to_fetch=ftp_files_to_fetch, **kwargs)

    @helpers.step
    def get_files_or_search_to_fetch(self):
        return self.get_ftp_files_or_search_to_fetch()

    @abstractmethod
    def get_ftp_files_or_search_to_fetch(self):
        pass

    @property
    def file_server(self):
        return self.ftp_server


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
    file_pattern = '*.xls'
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
