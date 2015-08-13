import sys


class ImporterRunningMixin(object):
    """
    Helper functionality to run an importing job
    """

    test_defaults = {}
    """
    Default test arguments
    """

    @classmethod
    def run(cls, *args, **kwargs):
        """
        Run the import, creating a job context
        """

        importer = cls(*args, **kwargs)
        importer.run_import()

    @classmethod
    def run_from_command_line(cls, sysargs=None):
        """
        Run the import, taking arguments from the command line
        """

        if sysargs is None:
            sysargs = sys.argv[1:]
        kwargs = cls.kwargs_from_command_line(sysargs)
        cls.run(**kwargs)

    @classmethod
    def test(cls, *args, **kwargs):
        """
        Test the import creating a test job context
        """

        test_kwargs = dict(cls.JobSettings.test_defaults)
        test_kwargs.update(kwargs)

        importer = cls(*args, **test_kwargs)
        importer.test_import()

    @classmethod
    def test_from_command_line(cls, sysargs=None):
        """
        Test the import, taking arguments from the command line
        """

        if sysargs is None:
            sysargs = sys.argv[1:]
        kwargs = cls.kwargs_from_command_line(sysargs)
        cls.test(**kwargs)

    @classmethod
    def kwargs_from_command_line(cls, sysargs):
        """
        Decompose kwargs from command line

        We allow two formats:

        * For single string values:
            parameter=value

            which results to {"parameter": "value"}

        * For list of string values:
            parameter[]=value1 parameter[]=value2

            which results to {"parameter": ["value1", "value2"]}

        So for example:
            simple=value list[]=first list[]=second singleton[]=alone

        results to {
            "simple": "value",
            "list": ["first", "second"],
            "singleton": ["alone"],
        }
        """

        splitted_kwargs = [kwarg.split('=') for kwarg in sysargs]
        kwargs_list = [
            (splitted_kwarg[0], '='.join(splitted_kwarg[1:]))
            for splitted_kwarg in splitted_kwargs
        ]
        kwargs_lists = {
            key_aggregate: [
                value
                for key, value in kwargs_list
                if key_aggregate == key
            ]
            for key_aggregate in set(key for key, _ in kwargs_list)
        }
        kwargs = {}
        for key_aggregate, values in kwargs_lists.iteritems():
            if key_aggregate.endswith('[]'):
                key = key_aggregate[:-2]
                value = values
            else:
                key = key_aggregate
                value = values[0]
                if len(values) != 1:
                    raise Exception("You defined '%(key)s' multiple times:\n"
                                    "Define only in one format:\n"
                                    "  %(key)s=value for a single value, or\n"
                                    "  %(key)s[]=value1 %(key)s[]=value2 "
                                    "for list" % {'key': key})

            if key in kwargs:
                raise Exception("You defined both '%(key)s' and '%(key)s[]':\n"
                                "Define only in one format:\n  %(key)s=value for a "
                                "single value, or\n  %(key)s[]=value1 "
                                "%(key)s[]=value2 for list" % {'key': key})

            kwargs[key] = value

        return kwargs
