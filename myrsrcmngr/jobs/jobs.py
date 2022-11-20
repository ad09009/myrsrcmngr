from libnmap.process import NmapProcess
from libnmap.parser import NmapParser
import os
from datetime import datetime, timedelta
from time import sleep
from django.utils import timezone


#import models
from website.models import scans, resourcegroups, hosts, reports, services, services_added_removed, changes

def new_parse(xml_result, filepath, scanid):
    status = True
    newrep = 0
    try:
        rgroup = resourcegroups.objects.get(scans__id=scanid)
        scanretrieved = scans.objects.get(id=scanid)
    except:
        print("necessary objects - rgroup and scan - not found")
        status = False
    try:
        newrep = NmapParser.parse_fromstring(xml_result)
    except:
        print("could not parse new report from string")
        status = False
    if status:
        try:
            created_rep = reports.objects.create(
                        resourcegroups_id = rgroup,
                        started_int = newrep.started,
                        endtime_int = newrep.endtime,
                        started_str = newrep.startedstr,
                        endtime_str = newrep.endtimestr,
                        version = newrep.version,
                        scan_type = newrep.scan_type,
                        num_services = newrep.numservices,
                        elapsed = newrep.elapsed,
                        hosts_up = newrep.hosts_up,
                        hosts_down = newrep.hosts_down,
                        hosts_total = newrep.hosts_total,
                        summary = newrep.summary,
                        full_cmndline = newrep.commandline,
                        path_to = filepath,
                        is_consistent = newrep.is_consistent(),
                        scan_id = scanretrieved,
                        is_last = True,
                        parse_success = status
            )
            return (created_rep, newrep)
        except:
            print("parsing or report insert failed")
            status = False
    failed_rep = reports.objects.create(
                        summary = "Report parsing failed",
                        path_to = filepath,
                        is_last = False,
                        parse_success = status
    )
    return (failed_rep, newrep)

def get_prev_rep(scanid):
    previous = 0
    oldrep = 0
    try:
        previous = reports.objects.filter(scan_id=scanid, is_last=True)[0]
        try:
            oldrep = NmapParser.parse_fromfile(previous.path_to)
        except:
            print("could not parse previous from file")
            oldrep = 0
    except:
        print("did not find i guess")
        previous = 0
    return (previous, oldrep)

def main_input(newrep, created_rep):
    
    for ahost in newrep.hosts:
        
        defaults_hosts = {
                    'mac':ahost.mac,
                    'vendor':ahost.vendor,
                    'ipv6':ahost.ipv6,
                    'status':ahost.status,
                    'hostnames':", ".join(ahost.hostnames),
                    'os_fingerprint':ahost.os_fingerprint,
                    'tcpsequence':ahost.tcpsequence,
                    'ipsequence':ahost.ipsequence,
                    'uptime':ahost.uptime,
                    'lastboot':ahost.lastboot,
                    'distance':ahost.distance,
                    'resourcegroup_id':created_rep.resourcegroups_id
        }
        host_obj, host_created = hosts.objects.update_or_create(main_address=ahost.address, defaults=defaults_hosts)
        created_rep.hosts_set.add(host_obj)
        for aserv in ahost.services:
            defaults_services = {
                    'protocol':aserv.protocol,
                    'state':aserv.state,
                    'name_conc':"{0}/{1} {2} {3}".format(aserv.port, aserv.protocol, aserv.state, aserv.service),
                    'reason':aserv.reason,
                    'reason_ip':aserv.reason_ip,
                    'reason_ttl':aserv.reason_ttl,
                    'service':aserv.service,
                    'owner':aserv.owner,
                    'banner':aserv.banner,
                    'servicefp':aserv.servicefp,
                    'tunnel':aserv.tunnel
            }
            serv_obj, serv_created = services.objects.update_or_create(host_id=host_obj, port=aserv.port, defaults=defaults_services)
            host_obj.services_set.add(serv_obj)
            created_rep.services_set.add(serv_obj)
            
    return True

def diff_input(newrep, oldrep):
    
    return True

def parse_call(xml_result, filepath, scanid):
    print("now we parse")
    #get prev rep id that had the scanid
    prev_tuple = get_prev_rep(scanid)
    previous = prev_tuple[0]
    oldrep = prev_tuple[1]
    #parse new report file
    rep_tuple = new_parse(xml_result, filepath, scanid)
    created_rep = rep_tuple[0]
    newrep = rep_tuple[1]
    if created_rep.parse_success:
        print("go with the rest")
        main_stat = main_input(newrep, created_rep)
        if previous and oldrep:
            print("we will do a diff")
            previous.is_last = False
            previous.save()
            diff_stat = diff_input(newrep, oldrep)
            
        else:
            print("no prev rep, so just the inserts please")
            
    else:
        print("new rep was not parsed")
        if previous:
            created_rep.prev_rep_id = previous.id    
            created_rep.save()
        return False
    return True


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
            if all_hosts.count() < 1:
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



