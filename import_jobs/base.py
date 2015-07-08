import sys

import utils

from infrastructure import context


class BaseImporter(object):
    """
    A basic interface for importers
    """

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
        mock_registry.register_auto_mocks_for_local_testing()

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
