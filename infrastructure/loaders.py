import csv

import utils
from mockable import Mockable
from context import with_new_section
from logging import log_method_call
from profiling import profile_method


class BaseLoader(Mockable):
    @utils.not_implemented
    def __init__(self, *args, **kwargs):
        pass

    @utils.not_implemented
    def get_all_data(self, filename):
        pass

    def __repr__(self):
        return self.__class__.__name__


class CsvLoader(BaseLoader):
    def __init__(self):
        pass

    @with_new_section
    @profile_method
    @log_method_call
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
