import csv
import xlrd
import datetime
from StringIO import StringIO
from abc import ABCMeta, abstractmethod

from infrastructure.context import helpers

from infrastructure.facilities.mocking import Mockable


class BaseLoader(Mockable):
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, *args, **kwargs):
        pass

    @abstractmethod
    def get_all_data_with_headers(self, filename):
        pass

    def __repr__(self):
        return self.__class__.__name__


class CsvLoader(BaseLoader):
    def __init__(self):
        pass

    @helpers.job_step
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


class ExcelLoader(BaseLoader):
    XLRD_WARNING_LOG_PREFIX = 'WARNING *** '
    XLRD_ERROR_LOG_PREFIX = 'ERROR *** '

    def __init__(self, sheet_index=0, skip_start_empty_rows=True,
                 skip_start_empty_columns=True):
        self.sheet_index = sheet_index
        self.skip_start_empty_rows = skip_start_empty_rows
        self.skip_start_empty_columns = skip_start_empty_columns

    @helpers.job_step
    def get_all_data_with_headers(self, filename):
        workbook = self._load_workbook(filename)
        sheet = workbook.sheet_by_index(self.sheet_index)
        first_row_index, first_column_index = \
            self._get_first_row_and_first_column_indexes(sheet)
        headers = \
            self._get_sheet_headers(sheet, first_row_index, first_column_index)
        data = self._get_sheet_data(sheet, headers, first_row_index,
                                    first_column_index)

        return data

    def _load_workbook(self, filename):
        logfile = StringIO()
        workbook = xlrd.open_workbook(filename, logfile=logfile)
        self._log_import_logs(logfile)

        return workbook

    @helpers.using_current_job("logger")
    def _log_import_logs(self, logger, logfile):
        for logline in logfile:
            if logline.startswith(self.XLRD_WARNING_LOG_PREFIX):
                logger.warn(logline[self.XLRD_WARNING_LOG_PREFIX:])
            elif logline.startswith(self.XLRD_ERROR_LOG_PREFIX):
                logger.error(logline[self.XLRD_ERROR_LOG_PREFIX:])

    def _get_first_row_and_first_column_indexes(self, sheet):
        if self.skip_start_empty_rows:
            for row_index in xrange(0, sheet.nrows):
                if not self._row_is_empty(sheet, row_index):
                    first_row_index = row_index
                    break
            else:
                # TODO: Perhaps we need to raise an error?
                first_row_index = sheet.nrows
        else:
            first_row_index = 0

        if self.skip_start_empty_columns:
            for column_index in xrange(0, sheet.ncols):
                if not self._column_is_empty(sheet, column_index):
                    first_column_index = column_index
                    break
            else:
                # TODO: Perhaps we need to raise an error?
                first_column_index = sheet.nrows
        else:
            first_column_index = 0

        return first_row_index, first_column_index

    def _row_is_empty(self, sheet, row_index):
        return all(
            sheet.cell(row_index, column_index).ctype == xlrd.biffh.XL_CELL_EMPTY
            for column_index in xrange(0, sheet.ncols)
        )

    def _column_is_empty(self, sheet, column_index):
        return all(
            sheet.cell(row_index, column_index).ctype == xlrd.biffh.XL_CELL_EMPTY
            for row_index in xrange(0, sheet.nrows)
        )

    def _get_sheet_headers(self, sheet, first_row_index, first_column_index):
        return [
            sheet.cell_value(first_row_index, column_index)
            for column_index in xrange(first_column_index, sheet.ncols)
        ]

    def _get_sheet_data(self, sheet, headers, first_row_index,
                        first_column_index):
        return (
            {
                header: self._get_sheet_cell_value(sheet, row_index, column_index)
                for column_index, header in enumerate(headers, first_column_index)
            }
            for row_index in xrange(first_row_index + 1, sheet.nrows)
        )

    def _get_sheet_cell_value(self, sheet, row, column):
        value = sheet.cell_value(row, column)

        cell_type = sheet.cell_type(row, column)

        if cell_type == xlrd.biffh.XL_CELL_DATE:
            value = self._get_sheet_cell_value_as_date(sheet, value)

        return value

    def _get_sheet_cell_value_as_date(self, sheet, value):
        date_tuple = xlrd.xldate_as_tuple(value, sheet.book.datemode)
        return datetime.datetime(*date_tuple)
