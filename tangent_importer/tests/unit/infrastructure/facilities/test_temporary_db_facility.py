import unittest

from tangent_importer import utils

from tangent_importer.import_jobs.base import Importer
from tangent_importer.infrastructure.facilities.temporary_db import TemporaryDB
from tangent_importer.infrastructure.facilities.mocking import MockRegistry
from tangent_importer.infrastructure.facilities.db_registry import DbRegistry
from tangent_importer.infrastructure.operations.savers import DbSaver

from tangent_importer.infrastructure.context import helpers

location = utils.make_location(__file__)

database = 'test'

class ImporterToTestSetupScriptImporter(Importer):
    uuid = '1000000000'
    class JobSettings(Importer.JobSettings):
        class TemporaryDBFacilitySettings(TemporaryDB.FacilitySettings):
            db_setup_scripts = {
                database: location("test_setup.sql"),
            }
            should_run = True

        class MockRegistryFacilitySettings(MockRegistry.FacilitySettings):
            no_mock_classes = [
                DbSaver.__name__,
            ]

    @helpers.step
    def do_run(self):
        pass


class TestTemporaryDBFacility(unittest.TestCase):
    def setUp(self):
        _, config = utils.get_config_module()
        database_info = config.db_registry[database]
        self.connection = DbRegistry.create_connection_to_database_from_info(database_info)
        self.cursor = self.connection.cursor()

    def test_setup_script(self):
        importer = ImporterToTestSetupScriptImporter()
        importer.test()

        self.cursor.execute("SELECT COUNT(*) FROM test_table")
        rows = self.cursor.fetchall()
        self.assertEquals(len(rows), 1)

    def tearDown(self):
        self.connection.close()



