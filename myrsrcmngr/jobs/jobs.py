from libnmap.process import NmapProcess
from libnmap.parser import NmapParser
import os
from datetime import datetime, timedelta
from time import sleep
from django.utils import timezone


#import models
from website.models import scans, resourcegroups, hosts, hosts_added_removed, reports, services, services_added_removed, changes

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
                        resourcegroup = rgroup,
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
                        scan = scanretrieved,
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
        previous = reports.objects.filter(scan=scanid, is_last=True)[0]
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
    try:
        for ahost in newrep.hosts:
            
            defaults_hosts = {
                        'ipv4':ahost.ipv4,
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
                        'resourcegroup':created_rep.resourcegroup
            }
            host_obj, host_created = hosts.objects.update_or_create(main_address=ahost.address, defaults=defaults_hosts)
            #print("inserted or upd host: ", host_obj, host_created)
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
                serv_obj, serv_created = services.objects.update_or_create(host=host_obj, port=aserv.port, defaults=defaults_services)
                #print("inserted or upd service: ", serv_obj, serv_created)
                host_obj.services_set.add(serv_obj)
                created_rep.services_set.add(serv_obj)
    except:
        print("something failed in main input")
        return False            
    return True

def nested_obj(objname):
    rval = None
    splitted = objname.split("::")
    if len(splitted) == 2:
        rval = splitted
    return rval

def diff_input(newrep, oldrep, created_rep, previous):
    print("here i will do the diff")
    rep_ndiff = newrep.diff(oldrep)
    print(newrep)
    print(oldrep)
    print(rep_ndiff)
    print(rep_ndiff.changed())
    for attr in rep_ndiff.changed():
        if "::" not in attr:
            attr_change = changes.objects.create(
                attribute = attr,
                cur_val = str(getattr(newrep, attr)),
                prev_val = str(getattr(oldrep, attr)),
                status = "CHANGED",
                cur_report = created_rep,
                prev_rep = previous.id
            )
            print("attr_change: ", attr, attr_change)
            print("one more time: ", attr)
        else:
            print("this never happens?")
            nested = nested_obj(attr)
            if nested is not None:
                if nested[0] == "NmapHost":
                    curhost = newrep.get_host_byid(nested[1])
                    prevhost = oldrep.get_host_byid(nested[1])
                    host_diff = curhost.diff(prevhost)
                    #added services
                    #print("{0} host has the following added services:".format(curhost.address))
                    for addserv in host_diff.added():
                        nestserv = nested_obj(addserv)
                        if nestserv is not None:
                            if nestserv[0] == "NmapService":
                                #add service to db
                                aservice = curhost.get_service_byid(nestserv[1])
                                dbservice_a = services.objects.get(host__main_address=curhost.address, port=aservice.port)
                                servadr = services_added_removed.objects.create(
                                    cur_report=created_rep,
                                    service=dbservice_a,
                                    prev_report=previous,
                                    status="ADDED"
                                )
                                print("addserv: ", servadr)
                        else:
                            print("Was not expecting an attribute when parsing host diff added")
                    #print("{0} host has the following removed services:".format(curhost.address))
                    for remserv in host_diff.removed():
                        nestserv = nested_obj(remserv)
                        if nestserv is not None:
                            if nestserv[0] == "NmapService":
                                #add service to db
                                rservice = prevhost.get_service_byid(nestserv[1])
                                dbservice_r = services.objects.get(host__main_address=curhost.address, port=rservice.port)
                                servrem = services_added_removed.objects.create(
                                    cur_report=created_rep,
                                    service=dbservice_r,
                                    prev_report=previous,
                                    status="REMOVED"
                                )
                                print("remserv: ", servrem)
                        else:
                            print("Was not expecting an attribute when parsing host diff removed")
                    #print("Changes in host: {0} :".format(curhost.address))
                    for chserv in host_diff.changed():
                        nestedhost = nested_obj(chserv)
                        if nestedhost is not None:
                            if nestedhost[0] == "NmapService":
                                #for every changed service
                                cservice = curhost.get_service_byid(nestedhost[1])
                                pservice = prevhost.get_service_byid(nestedhost[1])
                                serv_diff = cservice.diff(pservice)
                                for servattr in serv_diff.changed():
                                    nestedserv = nested_obj(servattr)
                                    if nestedserv is not None:
                                        print("WTF?")
                                    else:
                                        dbcserv = services.objects.get(host__main_address=curhost.address, port=cservice.port)
                                        dbchost = dbcserv.host
                                        servattrch = changes.objects.create(
                                            attribute = servattr,
                                            cur_val = str(getattr(cservice, servattr)),
                                            prev_val = str(getattr(pservice, servattr)),
                                            status = "CHANGED",
                                            cur_report = created_rep,
                                            prev_rep = previous.id,
                                            host = dbchost,
                                            service = dbcserv
                                        )
                                        print("changes servattr: ", servattrch)
                                for addattr in serv_diff.added():
                                    print("Added under service changes: {0}".format(addattr))

                                
                                for remattr in serv_diff.removed():
                                    print("Removed under service changes: {0}".format(remattr))

                        else:
                            dbchost2 = hosts.objects.get(main_address=curhost.address)
                            chservch = changes.objects.create(
                                attribute = chserv,
                                cur_val = str(getattr(curhost, chserv)),
                                prev_val = str(getattr(prevhost, chserv)),
                                status = "CHANGED",
                                cur_report = created_rep,
                                prev_rep = previous.id,
                                host = dbchost2
                            )
                            print("changes chserv: ", chserv, chservch)
    
    #print("Added hosts and services: ")
    for add in rep_ndiff.added():
        nested = nested_obj(add)
        if nested is not None:
            if nested[0] == "NmapHost":
                ahost = newrep.get_host_byid(nested[1])
                dbhost_a = hosts.objects.get(main_address=ahost.address)
                hadr = hosts_added_removed.objects.create(
                    cur_report=created_rep,
                    host=dbhost_a,
                    prev_report=previous,
                    status="ADDED"
                )
                print("hostsadded", add, hadr)
                for aserv in ahost.services:
                    dbserv_a = services.objects.get(host__main_address=ahost.address, port=aserv.port)
                    sadr = services_added_removed.objects.create(
                        cur_report=created_rep,
                        service=dbserv_a,
                        prev_report=previous,
                        status="ADDED"
                    )
                    print("services added for added host", aserv, sadr)
                
    # print("Removed hosts and services: ")
    for rem in rep_ndiff.removed():
        nested = nested_obj(rem)
        if nested is not None:
            if nested[0] == "NmapHost":
                rhost = oldrep.get_host_byid(nested[1])
                dbhost_r = hosts.objects.get(main_address=rhost.address)
                hadrgone = hosts_added_removed.objects.create(
                    cur_report=created_rep,
                    host=dbhost_r,
                    prev_report=previous,
                    status="REMOVED"
                )
                print("removed host", rem, hadrgone)
                for rserv in rhost.services:
                    dbserv_r = services.objects.get(host_main_address=rhost.address, port=rserv.port)
                    sadrgone = services_added_removed.objects.create(
                        cur_report=created_rep,
                        service=dbserv_r,
                        prev_report=previous,
                        status="REMOVED"
                    )
                    print("services removed for removed host", rserv, sadrgone)
    print("Did not fail on the diff parse, wow")
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
        if not main_stat:
            print("stopping execution, after failed main_input")
            return False
        if previous and oldrep:
            print("we will do a diff")
            previous.is_last = False
            previous.save()
            created_rep.prev_rep = previous.id    
            created_rep.save()
            diff_stat = diff_input(newrep, oldrep, created_rep, previous)
            if diff_stat:
                print("wow, much success")
        else:
            print("no prev rep, so just the inserts please")
            
    else:
        print("new rep was not parsed")
        if previous:
            created_rep.prev_rep = previous.id    
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
        scan_subnet = active_scan.resourcegroup.subnet
        all_hosts = active_scan.resourcegroup.hosts_set.all()
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
                active_scan.task_name = nmaptask.name
                active_scan.task_status = nmaptask.status
                active_scan.task_etc = nmaptask.etc
                active_scan.task_progress = nmaptask.progress
                active_scan.save()
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



