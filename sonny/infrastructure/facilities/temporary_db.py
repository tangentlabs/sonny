from sonny.infrastructure.context import helpers

from sonny.infrastructure.facilities.base import Facility

from sonny.infrastructure.operations.savers import DbSaver


@helpers.register_facility("temporary_db")
class TemporaryDB(Facility):
    """
    Run DB setup and cleanup for the job
    """
    class FacilitySettings(Facility.FacilitySettings):
        db_setup_scripts = {}
        """
        The setup SQL script per database
        """
        db_cleanup_scripts = {}
        """
        The cleanup SQL script per database
        """
        should_run = False
        """
        Should the scripts run
        """

    def first_step(self, step):
        if not self.should_run():
            return

        with helpers.with_step(name="Preparing DB"):
            for db_name, script in self.facility_settings.db_setup_scripts.iteritems():
                self.job.logger.info('Preparing %s with %s', db_name, script)
                self.ensure_is_safe_to_run_on_db(db_name)
                DbSaver({
                    "database": db_name,
                    "file": script,
                }).save_no_data_multiple_queries()

    def last_step(self, step, exc_type, exc_value, traceback):
        if not self.should_run():
            return

        with helpers.with_step(name="Cleaning up DB"):
            for db_name, script in self.facility_settings.db_cleanup_scripts.iteritems():
                self.job.logger.info('Cleaning %s with %s', db_name, script)
                self.ensure_is_safe_to_run_on_db(db_name)
                DbSaver({
                    "database": db_name,
                    "file": script,
                }).save_no_data_multiple_queries()

    def ensure_is_safe_to_run_on_db(self, db_name):
        database = self.job.db_registry.get_database(db_name)
        if not database['is_disposable']:
            raise Exception("Cannot run temporary setup on a "
                            "non-disposable DB: %s" % db_name)

    def should_run(self):
        return self.facility_settings.should_run
