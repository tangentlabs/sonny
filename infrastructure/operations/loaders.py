import csv

import utils

from infrastructure import context

from infrastructure.facilities.mocking import Mockable


class BaseLoader(Mockable):
    @utils.must_be_implemented_by_subclasses
    def __init__(self, *args, **kwargs):
        pass

    @utils.must_be_implemented_by_subclasses
    def get_all_data_with_headers(self, filename):
        pass

    def __repr__(self):
        return self.__class__.__name__


class CsvLoader(BaseLoader):
    def __init__(self):
        pass

    @context.job_step_method
    def get_all_data_with_headers(self, filename):
        with open(filename, 'rb') as _file:
            data = self.get_all_data_with_headers_from_file(_file)
            for datum in data:
                yield datum

    def get_all_data_with_headers_from_file(self, _file):
        reader = csv.reader(_file, delimiter=',', skipinitialspace=True)

        headers = reader.next()

        for row in reader:
            datum = {
                header: value
                for header, value in zip(headers, row)
            }
            yield datum


import csv
import sys
import xlrd
import datetime
from ftplib import FTP
from StringIO import StringIO


class ExcelCellTypes(object):  # noqa
    DATE = 'date'

    MappingFromRaw = {
        3: DATE,
    }


class ExcelLoader(BaseLoader):
    XLRD_WARNING_LOG_PREFIX = 'WARNING *** '
    XLRD_ERROR_LOG_PREFIX = 'ERROR *** '

    def __init__(self, sheet_index=0):
        self.sheet_index = sheet_index

    @context.job_step_method
    def get_all_data_with_headers(self, filename):
        workbook = self._load_workbook(filename)
        sheet = workbook.sheet_by_index(self.sheet_index)
        headers = self._get_sheet_headers(sheet)
        data = self._get_sheet_data(sheet, headers, start_row=1)

        return data

    def _load_workbook(self, filename):
        logfile = StringIO()
        workbook = xlrd.open_workbook(filename, logfile=logfile)
        self._log_import_logs(logfile)

        return workbook

    @context.method_using_current_job("logger")
    def _log_import_logs(self, logger, logfile):
        for logline in logfile:
            if logline.startswith(self.XLRD_WARNING_LOG_PREFIX):
                logger.warn(logline[self.XLRD_WARNING_LOG_PREFIX:])
            elif logline.startswith(self.XLRD_ERROR_LOG_PREFIX):
                logger.error(logline[self.XLRD_ERROR_LOG_PREFIX:])

    def _get_sheet_headers(self, sheet):
        return [
            sheet.cell_value(0, column_index)
            for column_index in xrange(0, sheet.ncols)
        ]

    def _get_sheet_data(self, sheet, headers, start_row):
        return (
            {
                header: self._get_sheet_cell_value(sheet, row_index, column_index)
                for column_index, header in enumerate(headers)
            }
            for row_index in xrange(start_row, sheet.nrows)
        )

    def _get_sheet_cell_value(self, sheet, row, column):
        value = sheet.cell_value(row, column)

        cell_type_raw = sheet.cell_type(row, column)
        cell_type = ExcelCellTypes.MappingFromRaw.get(cell_type_raw)

        if cell_type == ExcelCellTypes.DATE:
            value = self._get_sheet_cell_value_as_date(sheet, value)

        return value

    def _get_sheet_cell_value_as_date(self, sheet, value):
        date_tuple = xlrd.xldate_as_tuple(value, sheet.book.datemode)
        return datetime.datetime(*date_tuple)
