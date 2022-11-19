from libnmap.process import NmapProcess
from libnmap.parser import NmapParser
import os
from datetime import datetime, timedelta
from time import sleep

#import models
from .models import *

def scan_call():
    #check for active scan
    try:
        active_scan = scans.objects.get(active=True) #just one active scan at the same time should be possible
    #if none write to log and exit
    except scans.DoesNotExist:
        print("No active scan") #replace with log
        return 0
    except scans.MultipleObjectsReturned:
        print("Multiple objects returned") #replace with log
        return 1

    #if active scan exists
    #take last_executed and ScanSchedule and current time 
    # and check if its time to execute
    current_time = datetime.now()
    next_at = active_scan.next_execution_at
    if current_time > next_at:
        #if not time to execute write to log and exit
        print("Not time to execute yet") #replace with log
        return 0
    else:
        #if its time to execute, 
        # take params or template and build nmap command with nmap parser lib
        options = active_scan.ScanTemplate
        
        #take all hosts or subnet
        scan_subnet = active_scan.resourcegroups_id.subnet
        all_hosts = active_scan.resourcegroups_id.hosts_set.all()
        if scan_subnet is not None:
            targets = scan_subnet
        else: 
            if len(all_hosts) < 1:
                print("no hosts to run nmap on") #replace with log
                return 1
            else:
                targets = all_hosts.values_list('main_address', flat=True)
        nmap_proc = NmapProcess(targets=targets, options=options)
        nmap_proc.run_background()
        while nmap_proc.is_running():
            nmaptask = nmap_proc.current_task
            if nmaptask:
                print(
                    "Task {0} ({1}): ETC: {2} DONE: {3}%".format(
                        nmaptask.name, nmaptask.status, nmaptask.etc, nmaptask.progress
                    )
                )
                sleep(2)
        full_path_archive = os.path.join(archpath, filename)
        full_path_logs = os.path.join(logpath, logname)

#run nmap and wait for result


#optionally store and/or display nmap process status while executing


#validate result when finished


#update db scans, save file, pass on to parser


#parser checks in db for id of previous scan for this resourcegroup

#if none exists, parses report just to upsert report data


#if prev scan and report exists, parses report to upsert data and do an insert after completing a diff with prev report


#saves in db, updates statuses



