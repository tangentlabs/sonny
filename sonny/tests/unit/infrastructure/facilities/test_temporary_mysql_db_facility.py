import unittest

from sonny import utils

from sonny.import_jobs.base import Importer
from sonny.infrastructure.facilities.temporary_db import TemporaryDB
from sonny.infrastructure.facilities.mocking import MockRegistry
from sonny.infrastructure.operations.savers import DbSaver
from sonny.infrastructure.operations.database import DatabaseAccess

from sonny.infrastructure.context import helpers

location = utils.make_location(__file__)

database = 'test_mysql'


class ImporterToTestSetupScriptImporterWithMysql(Importer):
    uuid = '5e648698-d651-11e5-ab30-625662870761'

    class JobSettings(Importer.JobSettings):
        class TemporaryDBFacilitySettings(TemporaryDB.FacilitySettings):
            db_setup_scripts = {
                database: location("test_setup_mysql.sql"),
            }
            should_run = True

        class MockRegistryFacilitySettings(MockRegistry.FacilitySettings):
            no_mock_classes = [
                DbSaver.__name__,
            ]

    @helpers.step
    def do_run(self):
        pass


class TestTemporaryMysqlDBFacility(unittest.TestCase):
    def setUp(self):
        _, config = utils.get_config_module()
        database_info = config.db_registry[database]
        self.connection = DatabaseAccess().create_connection_from_info(database_info)
        self.cursor = self.connection.cursor()

    def test_setup_script(self):
        importer = ImporterToTestSetupScriptImporterWithMysql()
        importer.test()

        self.cursor.execute("SELECT COUNT(*) FROM test_table")
        rows = self.cursor.fetchall()
        self.assertEquals(len(rows), 1)

    def tearDown(self):
        self.connection.close()



