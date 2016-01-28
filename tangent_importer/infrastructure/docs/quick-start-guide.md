Quick start guide
====

You can look into the [annotated version] for more commentary

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

Add it to [infrastructure/everything.py](https://github.com/tangentlabs/tangent-importer/blob/master/tangent_importer/infrastructure/everything.py)

```python
from infrastructure.facilityies import (
    ...
    hider,
    ...
)
```

[annotated version]: https://github.com/tangentlabs/tangent-importer/blob/master/tangent_importer/docs/annotated.md
