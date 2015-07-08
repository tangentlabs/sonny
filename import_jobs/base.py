import sys

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

    @classmethod
    def run_from_command_line(cls):
        sysargs = sys.argv[1:]
        args, kwargs = cls.args_and_kwargs_from_command_line(sysargs)
        cls.run(*args, **kwargs)

    @classmethod
    @context.create_for_job
    @context.method_using_current_job("mock_registry", "logger", "profiler")
    def test(cls, mock_registry, logger, profiler, *args, **kwargs):
        mock_registry.register_mocks_using_default_noops(
            FtpFetcher,
            LocalFileDeleter,
            DbSaver,
        )

        importer = cls(*args, **kwargs)
        importer.run_import()

        print '*********** LOGS: ***********'
        print logger

        print '*********** PROFILING: ***********'
        print profiler

    @classmethod
    def test_from_command_line(cls):
        sysargs = sys.argv[1:]
        args, kwargs = cls.args_and_kwargs_from_command_line(sysargs)
        cls.run(*args, **kwargs)

    @classmethod
    def from_command_line(cls):
        sysargs = sys.argv[1:]
        if not sysargs:
            cls.run()
            return

        mode, sysargs = sysargs[0], sysargs[1:]
        args, kwargs = cls.args_and_kwargs_from_command_line(sysargs)
        if mode == "test":
            cls.test(*args, **kwargs)
        elif mode == "run":
            cls.run(*args, **kwargs)
        else:
            raise Exception("If arguments are passed, the first argument "
                            "must be 'run' or 'test'")

    @classmethod
    def args_and_kwargs_from_command_line(cls, sysargs):
        if '--' not in sysargs:
            args = sysargs
            kwargs = {}

            return args, kwargs

        dash_dash_index = sysargs.index('--')
        args, kwargs_list = \
            sysargs[:dash_dash_index], sysargs[dash_dash_index + 1:]

        splitted_kwargs = [kwarg.split('=') for kwarg in kwargs_list]
        kwargs = {
            splitted_kwarg[0]: '='.join(splitted_kwarg[1:])
            for splitted_kwarg in splitted_kwargs
        }

        return args, kwargs

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

    test_files_to_fetch = None

    def __init__(self, files_to_fetch=None):
        if isinstance(files_to_fetch, (str, unicode)):
            self.files_to_fetch = [files_to_fetch]
        else:
            self.files_to_fetch = files_to_fetch

    @context.job_step_method
    def run_import(self):
        filenames = self._get_files_to_fetch()
        local_filenames = self.fetcher(self.ftp_registry, self.file_server).fetch_files(filenames)
        for local_filename in local_filenames:
            data = self._loader().get_all_data_with_headers(local_filename)
            data = dicts_to_tuples(self.insert_query_fields)(data)
            self.saver(self.db_registry, self.insert_query).save(data)
        self.deleter().delete_files(local_filenames)
        self.saver(self.db_registry, self.post_job_query).save_no_data()

    def _get_files_to_fetch(self):
        if self.files_to_fetch:
            filenames = self.files_to_fetch
        else:
            filenames = self.get_files_to_fetch()

        return filenames

    @context.job_step_method
    @utils.must_be_implemented_by_subclasses
    def get_files_to_fetch(self):
        """The filenames to fetch from the remote location"""
        pass

    @classmethod
    def test(cls, *args, **kwargs):
        if not args and not kwargs:
            if cls.test_files_to_fetch:
                args = cls.test_files_to_fetch

        super(FetchLoadInsertDeleteCleanupImporter, cls).test(*args, **kwargs)


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

    def __init__(self, ftp_files_to_fetch=None):
        super(FtpCsvDbImporter, self).__init__(ftp_files_to_fetch)

    @context.job_step_method
    def get_files_to_fetch(self):
        return self.get_ftp_files_to_fetch()

    @utils.must_be_implemented_by_subclasses
    def ftp_files_to_fetch(self):
        pass

    @property
    def file_server(self):
        return self.ftp_server
