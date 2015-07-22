import os
import fnmatch
from ftplib import FTP
import imaplib
import tempfile
from email import message_from_string
from email.parser import HeaderParser
from email.header import decode_header
from abc import ABCMeta, abstractmethod

from infrastructure import context

from infrastructure.facilities.mocking import Mockable


class BaseFileFetcher(Mockable):
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, *args, **kwargs):
        pass

    @abstractmethod
    def fetch_file(self, filename):
        return filename

    def fetch_files(self, filenames):
        return [
            self.fetch_file(filename)
            for filename in filenames
        ]

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

    @context.method_using_current_job("ftp_registry")
    def __enter__(self, ftp_registry):
        source = ftp_registry["servers"][self.source]
        host = ftp_registry["hosts"][source["host"]]
        user = host["users"][source["user"]]
        self.ftp = FTP(host["server"])
        self.ftp.login(user['username'], user['password'])

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

    @context.job_step_method
    def fetch_files(self, filenames):
        with FtpContextManager(self.source) as ftp:
            return self._fetch_files_with_ftp(ftp, filenames)

    @context.job_step_method
    def fetch_file(self, filename):
        with FtpContextManager(self.source) as ftp:
            return self._fetch_file_with_ftp(ftp, filename)

    @context.job_step_method
    def search_files(self, directory, pattern="*"):
        with FtpContextManager(self.source) as ftp:
            filenames = self._search_files_with_ftp(ftp, directory, pattern)
            filenames = [
                os.path.join(directory, filename)
                for filename in filenames
            ]

            return filenames

    @context.job_step_method
    def fetch_from_search(self, directory, pattern="*"):
        with FtpContextManager(self.source) as ftp:
            filenames = self._search_files_with_ftp(ftp, directory, pattern)

            return self._fetch_files_with_ftp(ftp, filenames)

    def _search_files_with_ftp(self, ftp, directory, pattern="*"):
        ftp.cwd(directory)
        filenames = ftp.nlst()
        filtered = self._filter_files_by_filename(filenames, pattern)

        return filtered

    def _fetch_files_with_ftp(self, ftp, filenames):
        return [
            self._fetch_file_with_ftp(ftp, filename)
            for filename in filenames
        ]

    def _fetch_file_with_ftp(self, ftp, filename):
        with TemporaryFileContextManager() as (local_filename, local_file):
            ftp.retrbinary('RETR %s' % filename, local_file.write)

        return local_filename

    def _filter_files_by_filename(self, filenames, pattern):
        return [
            filename
            for filename in filenames
            if fnmatch.fnmatch(filename, pattern)
        ]


class ImapContextManager(object):
    """
    Manage the opening and closing of an IMAP connection
    """

    def __init__(self, source, mailbox):
        self.source = source
        self.mailbox = mailbox
        self.connection = None

    @context.method_using_current_job("email_registry")
    def __enter__(self, email_registry):
        server = email_registry["servers"][self.source]
        host = email_registry["hosts"][server["host"]]
        user = host["users"][server["user"]]

        self.connection = imaplib.IMAP4_SSL(host["server"])
        self.connection.login(user["username"], user["password"])

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

    @context.job_step_method
    def fetch_file(self, filename):
        raise Exception("This fetcher doesn't support 'fetch_file'")

    @context.job_step_method
    def search_files(self, *args, **kwargs):
        raise Exception("This fetcher doesn't support 'search_files'")

    @context.job_step_method
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

    @context.job_step_method
    def fetch_file(self, filename):
        return filename

    @context.job_step_method
    def fetch_from_search(self, *args, **kwargs):
        return kwargs.get('filenames') or []

    @context.job_step_method
    def search_files(self, *args, **kwargs):
        return kwargs.get('filenames') or []
