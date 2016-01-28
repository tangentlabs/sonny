Annotated developer's guides:
====

You can look into the [quick start guide] for a TL;DR

# How To write an importer:

```python
import utils

# Use this helper function to load files relatively to the local directory
location = utils.make_location(__file__)


# Using a class-based importer provides some useful automation and boilerplate.
class MyImporter(Importer):
    # Per-importer settings, that can be overriden
    class JobSettings(Importer.JobSettings):
        # Override some settings of a particular facility
        class LoggerFacilitySettings(Logger.FacilitySettings):
            identation = '**'

        # You can pass some default arguments when running in test mode
        # Of course, you can always override them from the command line
        test_defaults = {
            'alert_when_line_size': 33,
        }

    # The main running function, it can be passed kwargs from the command line
    def do_run(self, alert_when_line_size=333):
        # Break your important steps into functions, with a step decorator, or
        # use the with syntaxt
        files = self.fetch_files()
        data = self.load_files(files)
        with helpers.with_step(name='filter_data'):
            data = filter(lambda x, y: x != 0, data)
            if len(data) == alert_when_line_size:
                # You can use any facility that job has
                self.job.logger.warn('That weird line count again')
        self.save_to_db(data)

    @step
    def fetch_files(self):
        return FTP.fetch()

    @step
    def load_files(self, files):
        return CSV.load(files)

    @step save_to_db(self, data):
        DB.insert(data)
```

# How to write an operator:

```python
# Allow the operator to be mocked, if it's more efficient in test runs
from infrastructure.facilities.mocking import Mockable

# Have an interface that all Operators need to conform to, so that you can
# write mocks, and othes can write other specialisations of it
class BaseOperator(Mockable):
    __metaclass__ = ABCMeta

    @abstractmethod
    def do_the_thing(self, *args):
        pass


# Mark a class as mockable is it's ineficient or inconvient to use for
# testing, and local data can be provided
@BaseOperator.auto_mock_for_local_testing
class FooOperator(BaseOperator):
    # Get the settings on initialisation, feed the data on `do_the_thing`
    # Expect and allow the instance to be used more than once, independently,
    # ie don't keep state relevant to each `do_the_thing` run
    def __init__(self, where_from):
        self.where_from = where_from

    # Use @step for the entry points
    @step
    def do_the_thing(self, *args):
        yesterday(you_said='tomorrow')


# Create a default mock Operator, that doesn't do expensive operations
# (eg it returns the filenames instead of fetching them)
@BaseOperator.register_default_noop
class NoOpOperator(BaseFileFetcher):
    @step
    def do_the_thing(self, *args):
        # No need to operate on the test data
        return args
```

# How to write a facility:

```python
# Use Facility interface, to know what you can provide
class Logger(Facility):
    # Per-importer settings, that can be overriden
    class FacilitySettings(Facility.FacilitySettings):
        identation = '  '

    def __init__(self):
        self.logs = []
        self.facility_settings = self.FacilitySettings

    def log(self, message):
        self.logs.append(message)

    # You can perform things around jobs
    def enter_job(self, job, facility_settings):
        self.facility_settings = facility_settings
        self.log('New job!')

    # Or steps
    def enter_step(self, step):
        self.log(self.facility_settings.identation + 'New step!')
```

```python
# You can modify steps functions, or simply do something with their arguments
# or return values
class Log5FirstLines(Facility):
    def wrap_step_function(self, step, func):
        @wraps(func)
        def decorated(*args, **kwargs):
            retval = func(*args, **kwargs)

            try:
                iterable = iter(retval)
            except TypeError:
                # Not an iterable
                return retval

            def spy_iterable():
                for i, x in zip(xrange(5), iterable):
                    # You can still access other facilities
                    step.job.logger.log('SPYING: %s' % x)
                    yield x

                for x in iterable:
                    yield x

            return spy_iterable

        return decorated
```

```python
# To automatically load it for all import jobs, you should add it in the
# infrastructure/everything.py
from infrastructure.facility import (
    ...
    logger,
    log5firstlines,
    ...
)
```

[quick start guide]: https://github.com/tangentlabs/tangent-importer/blob/master/tangent_importer/docs/quick-start-guide.md
