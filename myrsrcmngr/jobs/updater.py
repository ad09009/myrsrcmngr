from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from .jobs import scan_call
from .scanmanager import *


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(mainjob, 'interval', seconds=60)
    #if job status is running skip execution
    scheduler.start()