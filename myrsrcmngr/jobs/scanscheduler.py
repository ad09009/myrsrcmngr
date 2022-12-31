from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.events import EVENT_JOB_ADDED, EVENT_JOB_REMOVED
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger
from .scanrunner import *

class ScanScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.scheduler.add_job(self.check_for_new_scans, 'interval', seconds=7)
        self.scheduler.add_job(self.check_for_inactive_scans, 'interval', seconds=9)
        self.run()
        self.scheduler.start()

    def check_for_new_scans(self):
        # Retrieve the list of new scans that need to be scheduled
        new_scans = self.get_new_scans()

        # Iterate through the new scans
        for scan in new_scans:
            # Check if the scan is already scheduled
            if not self.scheduler.get_job(str(scan.id)):
                # If the scan is not scheduled, add it to the scheduler
                self.scheduler.add_job(scancaller, trigger=IntervalTrigger(minutes=scan.get_next_exec_interval()),  next_run_time=timezone.now(), id=str(scan.id), args=[scan,])

    def get_new_scans(self):
        return [scan for scan in scans.objects.filter(active=True).exclude(status=2) if scan.next_execution_at <= timezone.now()]

    def check_for_inactive_scans(self):
        # Query the database for scans with the "active" marker set to False
        inactive_scans = scans.objects.filter(active=False)
        
        # For each inactive scan, remove the associated job from the scheduler if it exists
        for scan in inactive_scans:
            if self.scheduler.get_job(str(scan.id)):
                self.scheduler.remove_job(str(scan.id))

    def job_added_callback(self, event):
        print("A new job was added to the scheduler:", event.job_id)

    def job_removed_callback(self, event):
        print("A job was removed from the scheduler:", event.job_id)

    def run(self):
        self.scheduler.add_listener(self.job_added_callback, EVENT_JOB_ADDED)
        self.scheduler.add_listener(self.job_removed_callback, EVENT_JOB_REMOVED)


def start():
    ScanScheduler()
