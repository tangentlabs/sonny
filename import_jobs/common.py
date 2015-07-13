from datetime import date
from abc import ABCMeta, abstractmethod

from infrastructure import context

from import_jobs.base import BaseImporter

from infrastructure.operations import fetchers
from infrastructure.operations import loaders
from infrastructure.operations import transformers
from infrastructure.operations import formatters
from infrastructure.operations import savers
from infrastructure.operations import file_deleters


class FetchLoadInsertDeleteCleanupImporter(BaseImporter):
    __metaclass__ = ABCMeta

    """
    As the name describes:
    * Fetch a file
    * Load it
    * Insert it into a data store
    * Delete the fetched files
    * Run a post-job script
    """
    file_server = None
    insert_query = None
    post_job_query = None

    fetcher = None
    _loader = None
    saver = None
    deleter = None

    test_files_to_fetch = None

    def __init__(self, files_to_fetch=None):
        if isinstance(files_to_fetch, (str, unicode)):
            self.files_to_fetch = [files_to_fetch]
        else:
            self.files_to_fetch = files_to_fetch

    @context.job_step_method
    def run_import(self):
        filenames_or_search_kwargs, is_pattern = self._get_files_or_search_to_fetch()
        if is_pattern:
            search_kwargs = filenames_or_search_kwargs
            local_filenames = self.fetcher(self.file_server).fetch_files_from_search(**search_kwargs)
        else:
            filenames = filenames_or_search_kwargs
            local_filenames = self.fetcher(self.file_server).fetch_files(filenames)

        for local_filename in local_filenames:
            data = self._loader().get_all_data_with_headers(local_filename)
            data = self.transform_data(data)
            self.saver(self.insert_query).save(data)
        self.deleter().delete_files(local_filenames)
        self.saver(self.post_job_query).save_no_data()

    @context.job_step_method
    def transform_data(self, data):
        return data

    def _get_files_or_search_to_fetch(self):
        if self.files_to_fetch:
            is_pattern = False
            filenames = self.files_to_fetch
        else:
            filenames, is_pattern = self.get_files_or_search_to_fetch()

        return filenames, is_pattern

    @context.job_step_method
    @abstractmethod
    def get_files_or_search_to_fetch(self):
        """
        The filenames, or search pattern, to fetch from the remote location
        """
        pass

    @classmethod
    def test(cls, *args, **kwargs):
        if not args and not kwargs:
            if cls.test_files_to_fetch:
                args = cls.test_files_to_fetch

        super(FetchLoadInsertDeleteCleanupImporter, cls).test(*args, **kwargs)


class FtpCsvDbImporter(FetchLoadInsertDeleteCleanupImporter):
    __metaclass__ = ABCMeta

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

    def __init__(self, ftp_files_to_fetch=None):
        super(FtpCsvDbImporter, self).__init__(
            files_to_fetch=ftp_files_to_fetch)

    @context.job_step_method
    def get_files_or_search_to_fetch(self):
        return self.get_ftp_files_or_search_to_fetch()

    @abstractmethod
    def get_ftp_files_or_search_to_fetch(self):
        pass

    @property
    def file_server(self):
        return self.ftp_server


class EmailLoadTransformInsertDeleteImporter(BaseImporter):
    __metaclass__ = ABCMeta

    """
    * Fetch today's files from email using config search params
    * Load them
    * Transform them
    * Insert them, potentionally in multiple queries
    * Delete the files
    """

    email_source = None
    file_pattern = '*.xls'
    insert_queries = None

    fetcher = fetchers.EmailFetcher
    _loader = loaders.ExcelLoader
    saver = savers.DbSaver
    file_deleter = file_deleters.LocalFileDeleter

    def __init__(self, _today=None, files_to_fetch=None):
        self._today = _today or date.today()
        self.files_to_fetch = files_to_fetch

    @context.job_step_method
    def run_import(self):
        search_kwargs = self.get_search_kwargs()
        local_filenames = self.fetcher(self.email_source, self.file_pattern)\
            .fetch_from_search('INBOX', **search_kwargs)
        for local_filename in local_filenames:
            data = self._loader().get_all_data_with_headers(local_filename)
            data = self.transform_data(data)

            if len(self.insert_queries) > 1:
                # TODO: Perhaps we should be loading the file twice, instead of
                # creating a potentionally big tuple in-memory?
                data = transformers.generator_to_tuples()(data)

            for insert_query in self.insert_queries:
                self.saver(insert_query).save(data)

        self.file_deleter().delete_files(local_filenames)

    @context.job_step_method
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
        return self.job_environment_config['email_search_query']

    @context.job_step_method
    def transform_data(self, data):
        return data
