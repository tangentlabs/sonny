Guide to importing framework
====

The point of this framework is to make allow to alter and monitor the behaviour
of importers uniformly, and transparently to the importers. It's usefulness
lies in the interfaces it provides for developers who want to write an Importer
to use various facilities, like logging or settings, and developers who want
to write a Facility.

TLDR - Quick copy-paste guide
====

You can find annotated developer's guides at the bottom of this file

## Importer:
```python
import utils

from import_jobs.base import Importer

from infrastructure.operations import fetchers
from infrastructure.operations import loaders
from infrastructure.operations import transformers
from infrastructure.operations import casters
from infrastructure.operations import savers

location = utils.make_location(__file__)


class MyImporter(Importer):
    class JobSettings(Importer.JobSettings):

        test_defaults = {
            "files_to_fetch": [location("sample.csv")],
        }

    @helpers.step
    def do_run(self, files_to_fetch=["daily_report.csv"]):
        local_filenames = fetchers.FtpFetcher("reportFtpServer").fetch_files(files_to_fetch)
        for filename in local_filenames:
            data = loaders.CsvLoader().get_all_data_with_headers(filename)
            data = transformers.cast_dicts_values({
                "date": casters.to_date("%d.%m.%Y")
            })(data)
            savers.DbSaver({
                "database": "yourDatabase",
                "file": location("insert_rows.sql"),
            }).save(data)

```

## Operation:

```python
from infrastructure.operations.loaders import BaseLoader


class OCRLoader(BaseLoader):
    @helpers.step
    def get_all_data_with_headers(self, filename):
        _file = OCRlib.load(filename)
        with _file.extract_tabular_data() as raw_data:
            for raw_datum in raw_data.rows:
                if not OCRlib.is_seperator(raw_datum):
                  yield dict(zip(raw_data.columns, raw_datum))
```

## Facility:

```python
from infrastructure.facilities.base import Facility

from infrastructure.context import helpers

@helpers.register_facility("hider")
class Hider(Facility):
    def wrap_func(self, func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            if kwargs.get('clearance', 'lowest') != 'higest':
                kwargs['data'] = (
                    x, y, z
                    for x, y, z in kwargs['data']
                    if x != 'top_secret'
                )

            return func(*args, **kwargs)

        return wrapped
```

Add it to [infrastructure/everything.py](https://github.com/tangentlabs/tangent-importer/blob/develop/infrastructure/everything.py)

```python
from infrastructure.facilityies import (
    ...
    hider,
    ...
)
```

Philosophy behind the choices:
====

## Automatic reuse of functionality and workflow

As a lot of functionality is **universal to all importing jobs** (eg profiling, notifying),
and we want to have the ability to **add such functionality, without changing the
importers** (eg log the first 5 lines of data, alert if data doesn't "look like" historic
records), we use **dependency injection and inversion of control**.

## Transparency between layers of importing

The importer doesn't need to know about such a functionality, but can use it if necessary
(eg logging, config), even define importer-specifc overrides for it.

## Separation of concerns

We use a different piece of code for each type of fucntionality or operation, in order to
make it more testable and re-usable. To do this, we define very few points of interfacing
and conventions.

# Layers structure

There are 4 layers of functionality:

1. Context: the mediator between Operations/Importers and Facilities - everything shoud pass through it
2. Facilities: Importer-generic functionality, that operates on `Job` and `Step` signals
3. Operations: Bundled up pieces of importing (eg FTP fetching, CSV loading)
4. Importers: Steps of Operations to perform a specific (or generic) import

All of these layers should communicate through the following interfaces:

## An importer

1. Should be a subclass of [Importer](https://github.com/tangentlabs/tangent-importer/blob/develop/import_jobs/base.py)
2. Should implement `do_run` with a `@helpers.step` decorator
3. Every step that is distinct and a part of the data flow should be decorated or inside a `with` statement of `step`
4. Can provide overrides for specific facilities via `JobSettings`
5. Can access any facility by `self.job.<facility>`
6. Should pass around generators for data, not huge lists/tuples

## An operation

1. Should encapsulate a single atomic operation
2. Should use `step` decorators/with statements for logging/profiling substeps
3. Can access facilities via `helpers.get_current_job().<facility>`
4. Should provide an interface which implements, allowing specialisations
5. Should provide a no-op mock, if it makes sense for local testing

## A facility

1. Should be a subclass of [Facility](https://github.com/tangentlabs/tangent-importer/blob/develop/infrastructure/facilities/base.py)
2. Should use `facility_settings` to allow importers to override per-run settings
2. Should initialise in `enter_job`, and clean up in `exit_job`
3. Can use `enter_step` and `exit_step` to track steps
4. Can use `wrap_step` to manipulate the inputs and outputs of the step

Annotated developer's guides:
====

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
        with self.job.new_step(name='filter_data'):
            data = filter(lambda x, y: x != 0, data)
            if len(data) == alert_when_line_size:
                # You can use any facility that job has
                self.job.logger.warning('That weird line count again')
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
