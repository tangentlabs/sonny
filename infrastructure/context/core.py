class Context(object):
    """
    Registry for facilities that want to operate on jobs and steps, and job
    stack.
    Multiple jobs can run inside each other, and each job will have it's own
    facilities
    """
    def __init__(self):
        self.facility_classes = {}
        self._jobs = []

    @property
    def current_job(self):
        """
        The deepest nested job, that is currently running
        """
        return self._jobs[-1]

    def register_facility(self, name, klass):
        """
        Register a facility to be created every time a job is created
        """
        self.facility_classes[name] = klass

        return klass

    def find_facility_by_class_name(self, name):
        """
        Find a facility by matching fully or semi qualified class name
        """
        qualified_name = '.%s' % name
        for facility_name, klass in self.facility_classes.iteritems():
            klass_qualified_name = '.%s.%s' % (klass.__module__, klass.__name__)
            if klass_qualified_name.endswith(qualified_name):
                return klass

    def new_job(self, **kwargs):
        """
        Create a Job object, that must be used as a context manager, eg:

        with context.new_job():
            do_import()
        """
        job = Job(self, **kwargs)
        return job

    def _push_job(self, job):
        self._jobs.append(job)

    def _pop_job(self, job):
        popped = self._jobs.pop()
        assert popped == job


class Job(object):
    """
    Facilities holder for a job run, and step stack.

    Must be created with a context, and used as context manager, eg:

    with context.new_job():
        do_import()
    """
    def __init__(self, context, name, uuid, job_settings=None, test=False):
        self.name = name
        self.uuid = uuid
        self.job_settings = job_settings
        self.test = test
        self.context = context
        self._steps = []
        self._create_facilities()

    def __enter__(self):
        self.context._push_job(self)
        self._enter_facilities()
        self._first_step = self.new_step(name='<root>', is_first=True)
        self._first_step.__enter__()

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._first_step.__exit__(exc_type, exc_value, traceback)
        self._exit_facilities(exc_type, exc_value, traceback)
        self.context._pop_job(self)

    def _create_facilities(self):
        self.facilities = {
            name: facility_class()
            for name, facility_class
            in context.facility_classes.iteritems()
        }
        self.facilities_list = self.facilities.values()
        self.__dict__.update(self.facilities)

    def _enter_facilities(self):
        for facility in self.facilities_list:
            facility_settings = self._get_facility_settings_from_job(
                self.job_settings, facility.__class__)
            facility.enter_job(self, facility_settings)

    @classmethod
    def _get_facility_settings_from_job(cls, job_settings, facility_class):
        default = facility_class.FacilitySettings
        custom_name = '%sFacilitySettings' % facility_class.__name__
        return getattr(job_settings, custom_name, default)

    def _exit_facilities(self, exc_type, exc_value, traceback):
        for facility in self.facilities_list[::-1]:
            facility.exit_job(self, exc_type, exc_value, traceback)

    @property
    def current_step(self):
        if self._steps:
            return self._steps[-1]
        else:
            return self._first_step

    def new_step(self, **kwargs):
        step = Step(self, **kwargs)
        return step

    def _push_step(self, step):
        self._steps.append(step)

    def _pop_step(self, step):
        popped = self._steps.pop()
        assert popped == step


class Step(object):
    """
    A district and import step of a job
    """
    def __init__(self, job, name, is_first=False):
        self.job = job
        self.name = name
        if self.name is None:
            self.name = "<Job step>"
        self.depth = None
        self.is_first = is_first

    def __enter__(self):
        if self.is_first:
            self._enter_facilities_first_step()

        self.job._push_step(self)
        self.depth = len(self.job._steps)
        self._enter_facilities()

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._exit_facilities(exc_type, exc_value, traceback)
        self.job._pop_step(self)

        if self.is_first:
            self._exit_facilities_last_step(exc_type, exc_value, traceback)

    def _enter_facilities(self):
        for facility in self.job.facilities_list:
            facility.enter_step(self)

    def _enter_facilities_first_step(self):
        for facility in self.job.facilities_list:
            facility.first_step(self)

    def _exit_facilities(self, exc_type, exc_value, traceback):
        for facility in self.job.facilities_list[::-1]:
            facility.exit_step(self, exc_type, exc_value, traceback)

    def _exit_facilities_last_step(self, exc_type, exc_value, traceback):
        for facility in self.job.facilities_list[::-1]:
            facility.last_step(self, exc_type, exc_value, traceback)

    def wrap_step_function(self, func):
        wrapped = func
        for facility in self.job.facilities_list:
            wrapped = facility.wrap_step(self, wrapped)

        return wrapped


context = Context()
