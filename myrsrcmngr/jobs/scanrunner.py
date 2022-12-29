#import models
from website.models import scans, resourcegroups, hosts, hosts_added_removed, reports, services, services_added_removed, changes

from django.utils import timezone
from libnmap.process import NmapProcess
from libnmap.parser import NmapParser
import os
from datetime import datetime
from django.conf import settings
from time import sleep
    
def scancaller(scan):
    scanrun = ScanRunner(scan)
    if scanrun.error:
        print(f"Error in scanning or parsing scan {scan.id} {scan.scanName} for resource group {scan.resourcegroup.name}")

class ScanRunner:
    def __init__(self, scan):
        self.scan = scan
        self.error = 0
        self.scanid = scan.id
        self.xml_result = None
        self.report_path = None
        self.main()
    
    def main(self):
        if self.scan_call():
            print("scan complete, parsing results")
            if self.parse_call():
                print("Scan results parsed")
            else:
                print("Did not parse some scan results")
                self.error = 1
        else:
            print("Error in scan call")
            self.error = 1
            
    def parse_call(self):
        
        print(f"parsing file at {self.report_path} for scan id {self.scanid}")
        #get prev rep id that had the scanid
        prev_tuple = self.get_prev_rep()
        previous = prev_tuple[0]
        oldrep = prev_tuple[1]
        #parse new report file
        rep_tuple = self.new_parse()
        created_rep = rep_tuple[0]
        newrep = rep_tuple[1]
        if created_rep.parse_success:
            print("go with the rest")
            main_stat = self.main_input(newrep, created_rep)
            if not main_stat:
                print("stopping execution, after failed main_input")
                return False
            if previous and oldrep:
                print("we will do a diff")
                previous.is_last = False
                previous.save()
                created_rep.prev_rep = previous.id    
                created_rep.save()
                diff_stat = self.diff_input(newrep, oldrep, created_rep, previous)
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
    
    def get_prev_rep(self):
        previous = 0
        oldrep = 0
        try:
            previous = reports.objects.filter(scan=self.scanid, is_last=True)[0]
            try:
                oldrep = NmapParser.parse_fromfile(previous.path_to)
            except:
                print("could not parse previous from file")
                oldrep = 0
        except:
            print("did not find i guess")
            previous = 0
        return (previous, oldrep)
    
    def new_parse(self):
        xml_result = self.xml_result
        filepath =  self.report_path
        scanid = self.scanid
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
    
    def main_input(self, newrep, created_rep):
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
    
    def nested_obj(self, objname):
        rval = None
        splitted = objname.split("::")
        if len(splitted) == 2:
            rval = splitted
        return rval
    
    def diff_input(self, newrep, oldrep, created_rep, previous):
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
                nested = self.nested_obj(attr)
                if nested is not None:
                    if nested[0] == "NmapHost":
                        curhost = newrep.get_host_byid(nested[1])
                        prevhost = oldrep.get_host_byid(nested[1])
                        host_diff = curhost.diff(prevhost)
                        #added services
                        #print("{0} host has the following added services:".format(curhost.address))
                        for addserv in host_diff.added():
                            nestserv = self.nested_obj(addserv)
                            if nestserv is not None:
                                if nestserv[0] == "NmapService":
                                    #add service to db
                                    aservice = curhost.get_service_byid(nestserv[1])
                                    dbservice_a = services.objects.get(host__main_address=curhost.address, port=aservice.port)
                                    host_to_serv = hosts.objects.get(main_address=curhost.address)
                                    servadr = services_added_removed.objects.create(
                                        cur_report=created_rep,
                                        service=dbservice_a,
                                        prev_report=previous,
                                        status="ADDED"
                                    )
                                    serv_in_changes = changes.objects.create(
                                        cur_report=created_rep,
                                        service=dbservice_a,
                                        prev_rep=previous.id,
                                        host = host_to_serv,
                                        status="ADDED"
                                    )
                                    print("addserv: ", servadr)
                                    print("serv_in_changes: ", serv_in_changes)
                            else:
                                print("Was not expecting an attribute when parsing host diff added")
                        #print("{0} host has the following removed services:".format(curhost.address))
                        for remserv in host_diff.removed():
                            nestserv = self.nested_obj(remserv)
                            if nestserv is not None:
                                if nestserv[0] == "NmapService":
                                    #add service to db
                                    rservice = prevhost.get_service_byid(nestserv[1])
                                    dbservice_r = services.objects.get(host__main_address=curhost.address, port=rservice.port)
                                    host_from_serv = hosts.objects.get(main_address=curhost.address)
                                    servrem = services_added_removed.objects.create(
                                        cur_report=created_rep,
                                        service=dbservice_r,
                                        prev_report=previous,
                                        status="REMOVED"
                                    )
                                    remserv_in_changes = changes.objects.create(
                                        cur_report=created_rep,
                                        service=dbservice_r,
                                        prev_rep=previous.id,
                                        host = host_from_serv,
                                        status="REMOVED"
                                    )
                                    print("remserv_in_changes: ", remserv_in_changes)
                                    print("remserv: ", servrem)
                            else:
                                print("Was not expecting an attribute when parsing host diff removed")
                        #print("Changes in host: {0} :".format(curhost.address))
                        for chserv in host_diff.changed():
                            nestedhost = self.nested_obj(chserv)
                            if nestedhost is not None:
                                if nestedhost[0] == "NmapService":
                                    #for every changed service
                                    cservice = curhost.get_service_byid(nestedhost[1])
                                    pservice = prevhost.get_service_byid(nestedhost[1])
                                    serv_diff = cservice.diff(pservice)
                                    for servattr in serv_diff.changed():
                                        nestedserv = self.nested_obj(servattr)
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
            nested = self.nested_obj(add)
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
                    hadr_ch = changes.objects.create(
                        cur_report=created_rep,
                        host=dbhost_a,
                        prev_rep=previous.id,
                        status="ADDED"
                    )
                    print("hostsadded", add, hadr_ch)
                    for aserv in ahost.services:
                        dbserv_a = services.objects.get(host__main_address=ahost.address, port=aserv.port)
                        sadr = services_added_removed.objects.create(
                            cur_report=created_rep,
                            service=dbserv_a,
                            prev_report=previous,
                            status="ADDED"
                        )
                        sadr_ch = changes.objects.create(
                            cur_report=created_rep,
                            service=dbserv_a,
                            host=dbhost_a,
                            prev_rep=previous.id,
                            status="ADDED"
                        )
                        print("services added for added host", aserv, sadr, sadr_ch)
                    
        # print("Removed hosts and services: ")
        for rem in rep_ndiff.removed():
            nested = self.nested_obj(rem)
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
                    hadrgone_ch = changes.objects.create(
                        cur_report=created_rep,
                        host=dbhost_r,
                        prev_rep=previous.id,
                        status="REMOVED"
                    )
                    print("removed host", rem, hadrgone_ch)
                    for rserv in rhost.services:
                        dbserv_r = services.objects.get(host_main_address=rhost.address, port=rserv.port)
                        sadrgone = services_added_removed.objects.create(
                            cur_report=created_rep,
                            service=dbserv_r,
                            prev_report=previous,
                            status="REMOVED"
                        )
                        sadrgone_ch = changes.objects.create(
                            cur_report=created_rep,
                            service=dbserv_r,
                            host = dbhost_r,
                            prev_rep=previous.id,
                            status="REMOVED"
                        )
                        print("services removed for removed host", rserv, sadrgone, sadrgone_ch)
        print("Did not fail on the diff parse, wow")
        return True
    
    def scan_call(self):
        print("Scanning", self.scan.get_target(), "with options", self.scan.ScanTemplate)
        
        # Do the scan here
        
        #Start the scan
        nmap_proc = NmapProcess(targets=self.scan.get_target(), options=self.scan.ScanTemplate, safe_mode=False)
        nmap_proc.run_background()
        
        #Set status to running
        self.scan.status = nmap_proc.state
        self.scan.save()
        
        #Update scan execution statuses
        while nmap_proc.is_running():
            nmaptask = nmap_proc.current_task
            if nmaptask:
                self.scan.task_name = nmaptask.name
                self.scan.task_status = nmaptask.status
                self.scan.task_etc = nmaptask.etc
                self.scan.task_progress = nmaptask.progress
                self.scan.save()
                sleep(1)
        #Update last execution time
        self.scan.last_executed = timezone.now()
        
        # Update the scan object
        
        #Update the next execution time
        self.scan.next_execution_at = self.scan.next_execution_calc()
        
        #Update the status
        self.scan.status = nmap_proc.state
        #if scan failed, set active to false
        if nmap_proc.state == 4:
            self.scan.active = False
        
        self.scan.save()
        
        ct_date = datetime.strftime(timezone.now(), '%Y_%m_%d_%H_%M_%s')
        # Save the logs in a file
        log_result = nmap_proc.stderr
        logname = f"log_{self.scan.scanName}_{ct_date}.log"
        log_path = self.save_nmap_report_or_log(log_result, logname, "log")
        
        # Save the report in a file
        xml_result = nmap_proc.stdout
        filename = f"scan_{self.scan.scanName}_{ct_date}.xml"
        report_path = self.save_nmap_report_or_log(xml_result, filename, "report")
        if report_path:
            print("Report saved to", report_path)
            self.xml_result = xml_result
            self.report_path = report_path            
            return True
        else:
            return False
        
    def save_nmap_report_or_log(self, report_content, report_name, mode):
        # Create the folder to save the report if it doesn't exist
        if mode == "report":
            dir = "reports"
            ext = ".xml"
        elif mode == "log":
            dir = "logs"
            ext = ".log"
        else:
            return False
        try:
            report_folder = os.path.join(settings.BASE_DIR, dir)
            if not os.path.exists(report_folder):
                os.makedirs(report_folder)

            # Save the report to the folder
            report_path = os.path.join(report_folder, report_name + ext)
            with open(report_path, 'w') as report_file:
                report_file.write(report_content)
            return report_path
        except:
            print("Failed to create report or log file")
            return False