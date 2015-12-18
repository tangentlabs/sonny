import os
import fnmatch
from ftplib import FTP, error_perm
import imaplib
import tempfile
from email import message_from_string
from email.parser import HeaderParser
from email.header import decode_header
from abc import abstractmethod

from infrastructure.context import helpers

from infrastructure.operations.base import BaseOperation
import re


class BaseFileFetcher(BaseOperation):
    @abstractmethod
    def fetch_file(self, filename):
        return filename

    @abstractmethod
    def fetch_file_that_exists(self, filename):
        """
        Return a file if it exists, else return an appropriate exception, if
        that specifc file could not be fetched (eg permissions, doesn't exist),
        without raising it.

        If there was another error, non-specific to the file (eg connection
        error, out of disk space), still raise the exception
        """
        return filename, None

    def fetch_files(self, filenames):
        return map(self.fetch_file, filenames)

    def fetch_files_that_exist(self, filenames):
        return map(self.fetch_file_that_exists, filenames)

    @abstractmethod
    def search_files(self, *args, **kwargs):
        pass

    @abstractmethod
    def fetch_from_search(self, *args, **kwargs):
        pass

    def __repr__(self):
        return self.__class__.__name__


class FtpContextManager(object):
    """
    Manage the opening and closing of an FTP connection
    """

    def __init__(self, source):
        self.source = source
        self.ftp = None

    def __enter__(self):
        job = helpers.get_current_job()
        source = job.ftp_registry.get_ftp_server(self.source)
        self.ftp = FTP(source["server"])
        self.ftp.login(source['username'], source['password'])

        return self.ftp

    def __exit__(self, _type, value, traceback):
        self.ftp.close()
        self.ftp = None


class TemporaryFileContextManager(object):
    """
    Manage the creating, opening and closing of a temporary filename
    """

    def __init__(self, suffix=''):
        self.suffix = suffix

    def __enter__(self):
        _, local_filename = tempfile.mkstemp(suffix=self.suffix)
        self.local_file = open(local_filename, 'wb')

        return local_filename, self.local_file

    def __exit__(self, _type, value, traceback):
        self.local_file.__exit__(_type, value, traceback)


@BaseFileFetcher.auto_mock_for_local_testing
class FtpFetcher(BaseFileFetcher):
    def __init__(self, source):
        self.source = source

    @helpers.step
    def fetch_files(self, filenames):
        with FtpContextManager(self.source) as ftp:
            return self._fetch_files_with_ftp(ftp, filenames)

    @helpers.step
    def fetch_files_that_exist(self, filenames):
        with FtpContextManager(self.source) as ftp:
            return self._fetch_files_that_exist_with_ftp(ftp, filenames)

    @helpers.step
    def fetch_file(self, filename):
        with FtpContextManager(self.source) as ftp:
            return self._fetch_file(ftp, filename)

    @helpers.step
    def fetch_file_that_exists(self, filename):
        with FtpContextManager(self.source) as ftp:
            return self._fetch_file_that_exists_with_ftp(ftp, filename), None

    @helpers.step
    def search_files(self, directory, pattern="*"):
        with FtpContextManager(self.source) as ftp:
            filenames = self._search_files_with_ftp(ftp, directory, pattern)
            filenames = [
                os.path.join(directory, filename)
                for filename in filenames
            ]

            return filenames

    @helpers.step
    def search_regex_files(self, directory, regex):
        with FtpContextManager(self.source) as ftp:
            filenames = self._search_regex_files_with_ftp(ftp, directory, regex)
            filenames = [
                os.path.join(directory, filename)
                for filename in filenames
            ]

            return filenames

    @helpers.step
    def fetch_from_search(self, directory, pattern="*"):
        with FtpContextManager(self.source) as ftp:
            filenames = self._search_files_with_ftp(ftp, directory, pattern)

            return self._fetch_files_with_ftp(ftp, filenames)

    def _search_files_with_ftp(self, ftp, directory, pattern="*"):
        ftp.cwd(directory)
        filenames = ftp.nlst()
        filtered = self._filter_files_by_filename(filenames, pattern)

        return filtered

    def _search_regex_files_with_ftp(self, ftp, directory, regex):
        ftp.cwd(directory)
        filenames = ftp.nlst()
        filtered = self._filter_regex_files_by_filename(filenames, regex)

        return filtered

    def _fetch_files_with_ftp(self, ftp, filenames):
        return [
            self._fetch_file_with_ftp(ftp, filename)
            for filename in filenames
        ]

    def _fetch_files_that_exist_with_ftp(self, ftp, filenames):
        return [
            self._fetch_file_that_exists_with_ftp(ftp, filename)
            for filename in filenames
        ]

    def _fetch_file_with_ftp(self, ftp, filename):
        local_filename, exception = \
            self._fetch_file_that_exists_with_ftp(ftp, filename)

        if exception:
            helpers.get_current_job().logger.error(
                "Failed to get FTP file %s while in %s",
                filename, ftp.pwd())
            raise exception

        return local_filename

    def _fetch_file_that_exists_with_ftp(self, ftp, filename):
        with TemporaryFileContextManager() as (local_filename, local_file):
            try:
                ftp.retrbinary('RETR %s' % filename, local_file.write)
            except error_perm, e:
                return None, e

        return local_filename, None

    def _filter_files_by_filename(self, filenames, pattern):
        return [
            filename
            for filename in filenames
            if fnmatch.fnmatch(filename, pattern)
        ]

    def _filter_regex_files_by_filename(self, filenames, regex):
        return [
            filename
            for filename in filenames
            if re.match(regex, filename)
        ]


class ImapContextManager(object):
    """
    Manage the opening and closing of an IMAP connection
    """

    def __init__(self, source, mailbox):
        self.source = source
        self.mailbox = mailbox
        self.connection = None

    def __enter__(self):
        job = helpers.get_current_job()
        source = job.email_registry.get_email_server(self.source)

        self.connection = imaplib.IMAP4_SSL(source["server"])
        self.connection.login(source["username"], source["password"])

        self.connection.select(self.mailbox)

        return self.connection

    def __exit__(self, _type, value, traceback):
        self.connection.close()
        self.connection.logout()
        self.connection = None


@BaseFileFetcher.auto_mock_for_local_testing
class EmailFetcher(BaseFileFetcher):
    EMAIL_PART_HEADERS = '(BODY[HEADER])'
    EMAIL_PART_WHOLE = '(RFC822)'
    SEARCH_QUERY_FIELDS_MAPPING = {
        'Date': 'SentOn',
    }
    """
    Translate search parameters field name for IMAP search query
    """

    def __init__(self, source, pattern='*'):
        """
        :param patter: Case-insensitive pattern match the files fetched
        """
        self.source = source
        self.pattern = pattern.lower()
        self.header_parser = HeaderParser()

    @helpers.step
    def fetch_file(self, filename):
        raise Exception("This fetcher doesn't support 'fetch_file'")

    @helpers.step
    def fetch_file_that_exists(self, filename):
        raise Exception("This fetcher doesn't support 'fetch_file_that_exists'")

    @helpers.step
    def search_files(self, *args, **kwargs):
        raise Exception("This fetcher doesn't support 'search_files'")

    @helpers.step
    def fetch_from_search(self, maillbox, **search_params):
        with ImapContextManager(self.source, maillbox) as connection:
            message_ids = self._search_for_emails_in_server(
                connection, search_params)
            matched_message_ids = self._filter_matching_emails(
                connection, message_ids, search_params)
            attachments = self._fetch_messages_attachments(
                connection, matched_message_ids)
            filtered_attachments = self._filter_attachments_by_filename(
                attachments)
            local_filenames = self._save_attachments(filtered_attachments)

            return list(local_filenames)

    def _search_for_emails_in_server(self, connection, search_params):
        search_query = self._get_search_query(search_params)
        _, (message_ids_str,) = connection.search(None, search_query)
        message_ids = message_ids_str.split()

        for message_id in message_ids:
            yield message_id

    def _filter_matching_emails(self, connection, message_ids, search_params):
        for message_id in message_ids:
            headers = self._fetch_email_part(
                connection, message_id, self.EMAIL_PART_HEADERS)
            parsed_headers = self.header_parser.parsestr(headers)
            if self._headers_match_params(parsed_headers, search_params):
                yield message_id

    def _fetch_messages_attachments(self, connection, message_ids):
        for message_id in message_ids:
            _email = self._fetch_email_part(
                connection, message_id, self.EMAIL_PART_WHOLE)
            message = message_from_string(_email)
            if not message.is_multipart():
                continue

            attachments = message.get_payload()[1:]
            for attachment in attachments:
                yield attachment

    def _filter_attachments_by_filename(self, attachments):
        for attachment in attachments:
            filename = attachment.get_filename().lower()
            if fnmatch.fnmatch(filename, self.pattern):
                yield attachment

    def _save_attachments(self, attachments):
        for attachment in attachments:
            suffix = '-%s' % attachment.get_filename()
            with TemporaryFileContextManager(suffix=suffix)\
                    as (local_filename, local_file):
                local_file.write(attachment.get_payload(decode=True))
            yield local_filename

    def _fetch_email_part(self, connection, message_id, part):
        _, data = connection.fetch(message_id, part)
        _, part_data = data[0]

        return part_data

    def _get_search_query(self, search_params):
        return '(%s)' % ' '.join(
            '%s "%s"' %
            (self._normalise_header_name_for_query(header_name),
             self._escape_search_param(search_param))
            for header_name, search_param in search_params.iteritems()
        )

    def _normalise_header_name_for_query(self, header_name):
        normalised = header_name\
            .replace('__contains', '')
        normalised = self.SEARCH_QUERY_FIELDS_MAPPING.get(normalised, normalised)
        normalised = normalised.upper()

        return normalised

    def _escape_search_param(self, search_param):
        return search_param\
            .replace('\\', '\\\\')\
            .replace('"', '\\"')

    def _decode_headers(self, parsed_headers):
        return {
            header_name: decode_header(parsed_header)[0][0]
            for header_name, parsed_header in parsed_headers.iteritems()
        }

    def _headers_match_params(self, decoded_headers, search_params):
        return all(
            header_name in decoded_headers
            and len(decoded_headers[header_name]) == len(search_param)
            for header_name, search_param in search_params.iteritems()
            if not header_name.endswith("__contains")
        )


@BaseFileFetcher.register_default_noop
class NoOpFetcher(BaseFileFetcher):
    def __init__(self, *args, **kwargs):
        pass

    @helpers.step
    def fetch_file(self, filename):
        return filename

    @helpers.step
    def fetch_file_that_exists(self, filename):
        return filename, None

    @helpers.step
    def fetch_from_search(self, *args, **kwargs):
        return kwargs.get('filenames') or []

    @helpers.step
    def search_files(self, *args, **kwargs):
        return kwargs.get('filenames') or []
