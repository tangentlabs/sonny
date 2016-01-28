from infrastructure.context import helpers

from import_jobs.base import Importer


class RegisterJobsToDashboard(Importer):
    uuid = '10000000-1000-1000-1000-100000000000'
    is_testable = False

    @helpers.step
    def do_run(self):
        self.job.dashboard.discover_and_register_jobs()
