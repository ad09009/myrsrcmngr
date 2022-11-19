from libnmap.process import NmapProcess
from libnmap.parser import NmapParser
import os
from datetime import datetime, timedelta
from time import sleep
from django.utils import timezone


#import models
from website.models import scans, resourcegroups, hosts, reports, services, services_added_removed, changes


def parse_call(xml_result, filepath, scanid):
    print("now we parse")
    return 1

def scan_call():
    #check for active scan
    print("new job called")
    try:
        active_scan = scans.objects.get(active=True) #just one active scan at the same time should be possible
    #if none write to log and exit
    except scans.DoesNotExist:
        print("No active scan") #replace with log
        return 0
    except scans.MultipleObjectsReturned:
        print("Multiple objects returned") #replace with log
        return 1
    print("scan exists")
    if active_scan.status == 2:
        return 0
    #if active scan exists
    #take last_executed and ScanSchedule and current time 
    # and check if its time to execute
    current_time = timezone.now()
    next_at = active_scan.next_execution_at
    print("current: ", current_time)
    print("next: ",next_at)
    if current_time < next_at:
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
        nmap_proc = NmapProcess(targets=targets, options=options, safe_mode=False)
        nmap_proc.run_background()
        active_scan.status = nmap_proc.state
        active_scan.save()
        while nmap_proc.is_running():
            nmaptask = nmap_proc.current_task
            if nmaptask:
                print(
                    "Task {0} ({1}): ETC: {2} DONE: {3}%".format(
                        nmaptask.name, nmaptask.status, nmaptask.etc, nmaptask.progress
                    )
                )
                sleep(2)
        active_scan.last_executed = timezone.now()
        schedule = active_scan.ScanSchedule
        if schedule == 'hh':
            next_at_delta = timedelta(minutes=30)
        elif schedule == 'h':
            next_at_delta = timedelta(hours=1)
        elif schedule == 'd':
            next_at_delta = timedelta(days=1)
        elif schedule == 'w':
            next_at_delta = timedelta(days=7)
        else:
            next_at_delta = timedelta(minutes=15)
        active_scan.next_execution_at = timezone.now() + next_at_delta
        active_scan.status = nmap_proc.state
        if nmap_proc.state == 4:
            active_scan.active = False
        active_scan.save()
        
        scanname = active_scan.scanName
        scanid = active_scan.id
        ct_date = datetime.strftime(timezone.now(), '%Y_%m_%d_%H_%M_%s')
        filename = f"scan_{scanname}_{ct_date}.xml"
        logname = f"log_{scanname}_{ct_date}.log"
        archpath = "/home/kilikuku/Downloads/testnmap/myrsrcmngr/website/reports/"
        logpath = "/home/kilikuku/Downloads/testnmap/myrsrcmngr/website/logs/"
        full_path_archive = os.path.join(archpath, filename)
        full_path_logs = os.path.join(logpath, logname)
        xml_result = nmap_proc.stdout
        filepath = full_path_archive
        with open(full_path_archive, "w+") as fp:
            fp.write(nmap_proc.stdout)
        #print(nmap_proc.stderr)
        with open(full_path_logs, "w+") as fp:
            fp.write(nmap_proc.stderr)
        if (not os.path.isfile(full_path_archive)) or (not os.path.isfile(full_path_logs)):
            print("Failed to create xml or log file")
            return 5
        parse_status = parse_call(xml_result, filepath, scanid)
        if parse_status:
            print("got to the end")
            return 0
        else:
            print("did not parse")
            return 1
#run nmap and wait for result


#optionally store and/or display nmap process status while executing


#validate result when finished


#update db scans, save file, pass on to parser


#parser checks in db for id of previous scan for this resourcegroup

#if none exists, parses report just to upsert report data


#if prev scan and report exists, parses report to upsert data and do an insert after completing a diff with prev report


#saves in db, updates statuses

#use in_bulk, bulk_create, bulk_update



