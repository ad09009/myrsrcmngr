from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from .jobs import scan_call, parse_call

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(scan_call, 'interval', seconds=60)
    scheduler.start()