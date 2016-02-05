import sys

from sonny.infrastructure.context import helpers


class ImporterRunningMixin(object):
    """
    Helper functionality to run an importing job
    """

    test_defaults = {}
    """
    Default test arguments
    """

    is_testable = True
    """
    Whether this job should be ever tested
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

        importer_cls = cls.get_importer_class_from_command_line(sysargs)
        kwargs = importer_cls.kwargs_from_command_line(sysargs)
        importer_cls.run(**kwargs)

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

        importer_cls = cls.get_importer_class_from_command_line(sysargs)
        kwargs = importer_cls.kwargs_from_command_line(sysargs)
        importer_cls.test(**kwargs)

    @classmethod
    def kwargs_from_command_line(cls, sysargs):
        """
        Get kwargs overrides for an importer instance
        """
        sys_kwargs = [arg for arg in sysargs if not arg.startswith('--')]
        return cls.compose_args_from_command_line(sys_kwargs)

    @classmethod
    def get_importer_class_from_command_line(cls, sysargs):
        """
        Create an importer class with JobSettings overrides from the command
        line
        """
        job_settings = cls.job_settings_from_command_line(sysargs)

        return type(cls.__name__, (cls,), {'JobSettings': job_settings})

    @classmethod
    def job_settings_from_command_line(cls, sysargs):
        """
        Create JobSettings for an importer, with overrides from the command
        line
        """
        raw_facility_settings = cls\
            .raw_facilities_settings_from_command_line(sysargs)
        facilities_settings = [
            cls.create_overriden_facility_settings(
                arg_name[2:], overriden_facility_settings)
            for arg_name, overriden_facility_settings
            in raw_facility_settings.iteritems()
        ]
        facilities_settings_dict = {
            facility_settings.__name__: facility_settings
            for facility_settings in facilities_settings
        }

        return type('JobSettings', (cls.JobSettings,),
                    facilities_settings_dict)

    @classmethod
    def create_overriden_facility_settings(cls, facility_name,
                                           overriden_facility_settings):
        """
        Create FacilitySettings for a facility, with overrides from the command
        line
        """
        facility_class = helpers.find_facility_by_class_name(facility_name)
        if not facility_class:
            raise Exception("No known facility named '%s'" % facility_name)
        facility_settings = helpers.get_facility_settings_for_job(
            cls.JobSettings, facility_class)
        facility_job_settings_name = \
            '%sFacilitySettings' % facility_class.__name__

        overriden_facility_settings = type(facility_job_settings_name,
                                           (facility_settings,),
                                           overriden_facility_settings)

        return overriden_facility_settings

    @classmethod
    def raw_facilities_settings_from_command_line(cls, sysargs):
        """
        Facility settings overrides from command line. Same as class kwargs,
        but they need to be prefixed with '--', and include facility name and
        setting name:

        --FacilityName.setting_name=value
        --FacilityName.setting_name[]=value
        """
        sys_kwargs = [arg for arg in sysargs if arg.startswith('--')]
        kwargs = cls.compose_args_from_command_line(sys_kwargs)
        all_facility_settings = {}
        for name, value in kwargs.iteritems():
            try:
                facility_name, setting_name = name.split('.')
            except ValueError:
                raise Exception(
                    "Settings facilities must be in the following format:\n"
                    "--FacilityName.setting_name=value\n"
                    "--FacilityName.setting_name[]=value\n")

            facility_settings = all_facility_settings.setdefault(facility_name,
                                                                 {})
            facility_settings[setting_name] = value

        return all_facility_settings

    # This starts to get ridiculous. Perhaps replace with eval?
    # like: ./run.py importer kwargs='{"a": "b", "c": 1, "d": [2, "3", False]}'
    @classmethod
    def compose_args_from_command_line(cls, sysargs):
        """
        Decompose args from command line

        We allow two formats:

        * For single string values:
            parameter=value

            which results to {"parameter": "value"}

        * For list of string values:
            parameter[]=value1 parameter[]=value2

            which results to {"parameter": ["value1", "value2"]}

        * For boolean value:
            parameter?=True
            parameter?=False

            which results to {"parameter": True} and {"parameter": False}

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
            elif key_aggregate.endswith('?'):
                key = key_aggregate[:-1]
                value = {'True': True, 'False': False}[values[0]]
                if len(values) != 1:
                    raise Exception("You defined '%(key)s?' multiple times:\n"
                                    "Define only in one format:\n"
                                    "  %(key)s=value for a single value, or\n"
                                    "  %(key)s[]=value1 %(key)s[]=value2 for "
                                    "list, or\n  %(key)s?=value for boolean"
                                    % {'key': key})
            else:
                key = key_aggregate
                value = values[0]
                if len(values) != 1:
                    raise Exception("You defined '%(key)s' multiple times:\n"
                                    "Define only in one format:\n"
                                    "  %(key)s=value for a single value, or\n"
                                    "  %(key)s[]=value1 %(key)s[]=value2 for "
                                    "list, or\n  %(key)s?=value for boolean"
                                    % {'key': key})

            if key in kwargs:
                raise Exception("You defined more than one of '%(key)s', "
                                "'%(key)s!' and '%(key)s[]':\n"
                                "Define only in one format:\n  %(key)s=value "
                                "for a single value, or\n  %(key)s[]=value1 "
                                "%(key)s[]=value2 for list, or\n  "
                                "%(key)s?=value for boolean" % {'key': key})

            kwargs[key] = value

        return kwargs
