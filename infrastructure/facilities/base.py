class Facility(object):
    """
    Facility interface, for responding to running jobs and steps
    """

    class FacilitySettings(object):
        pass

    def enter_job(self, job, facility_settings):
        """
        Called when a job is about to start
        """
        self.job = job
        self.facility_settings = facility_settings

    def exit_job(self, job, exc_type, exc_value, traceback):
        """
        Called when a job is about to exit. If there was an exception, it is
        provided as arguments
        """
        pass

    def enter_step(self, step):
        """
        Called when a step is about to run
        """
        pass

    def wrap_step(self, step, func):
        """
        Wrap a step methhod/function, so that the facilit can access it's
        arguments, and it's return value
        """
        return func

    def exit_step(self, step, exc_type, exc_value, traceback):
        """
        Called when a step is about to exit. If there was an exception, it is
        provided as arguments
        """
        pass
