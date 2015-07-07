import csv

import utils

from infrastructure import context

from infrastructure.facilities.mocking import Mockable


class BaseLoader(Mockable):
    @utils.must_be_implemented_by_subclasses
    def __init__(self, *args, **kwargs):
        pass

    @utils.must_be_implemented_by_subclasses
    def get_all_data(self, filename):
        pass

    def __repr__(self):
        return self.__class__.__name__


class CsvLoader(BaseLoader):
    def __init__(self):
        pass

    @context.job_step_method
    def get_all_data(self, filename):
        with open(filename, 'rb') as _file:
            reader = csv.reader(_file, delimiter=',', quotechar='"')

            headers = reader.next()
            headers = map(str.strip, headers)

            for row in reader:
                datum = {
                    header: value.strip()
                    for header, value in zip(headers, row)
                }
                yield datum
