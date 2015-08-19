class Facility(object):
    """
    Facility interface, for responding to running jobs and steps
    """

    class FacilitySettings(object):
        pass

    def enter_job(self, job, facility_settings):
        """
        Called when a job is about to start

        At this point, no intra-facilities actions should be taken, as the
        order of execution is not guaranteed, and some facilities might not
        have started.
        """
        self.job = job
        self.facility_settings = facility_settings

    def exit_job(self, job, exc_type, exc_value, traceback):
        """
        Called when a job is ready to exit. If there was an exception, it is
        provided as arguments.

        At this point, no intra-facilities actions should be taken, as the
        order of execution is not guaranteed, and some facilities might have
        exited.
        """
        pass

    def first_step(self, step):
        """
        Called when a job has just started

        This is the first chance to do anything job-wide that uses other
        facilities.
        """
        pass

    def last_step(self, step, exc_type, exc_value, traceback):
        """
        Called when a job is about to exit. If there was an exception, it is
        provided as arguments.

        This is the last chance to do anything job-wide that uses other
        facilities.
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
