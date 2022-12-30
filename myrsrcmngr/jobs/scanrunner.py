#import models
from website.models import scans, resourcegroups, hosts, hosts_added_removed, reports, services, services_added_removed, changes

from django.utils import timezone
from libnmap.process import NmapProcess
from libnmap.parser import NmapParser
import os
from datetime import datetime
from django.conf import settings
from time import sleep
import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logpath = os.path.join(settings.BASE_DIR, 'scanrunner.log')
handler = logging.FileHandler(logpath)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def scancaller(scan):
    print('logger:', logger.level, logger.handlers)
    scanrun = ScanRunner(scan)
    if scanrun.error:
        logger.error(f"Error in scanning or parsing scan {scan.id} {scan.scanName} for resource group {scan.resourcegroup.name}")

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
            logger.info(f"scan {self.scanid} complete, parsing results")
            if self.parse_call():
                logger.info(f"Scan {self.scanid} results parsed")
            else:
                logger.error(f"Did not parse some scan {self.scanid} results, some failure in parse_call")
                self.error = 1
        else:
            logger.error(f"Error in scan {self.scanid} call")
            self.error = 1
            
    def parse_call(self):
        
        logger.info(f"parsing file at {self.report_path} for scan id {self.scanid}")
        #get prev rep id that had the scanid
        prev_tuple = self.get_prev_rep()
        previous = prev_tuple[0]
        oldrep = prev_tuple[1]
        #parse new report file
        logger.info(f"calling new_parse for scan id {self.scanid}")
        rep_tuple = self.new_parse()
        created_rep = rep_tuple[0]
        newrep = rep_tuple[1]
        if created_rep.parse_success:
            logger.info(f"go with the rest, new_parse was successful, report should be in db, scan id {self.scanid}, starting main_input")
            main_stat = self.main_input(newrep, created_rep)
            if not main_stat:
                logger.error(f"stopping execution of parse_call for {self.scanid}, after failed main_input")
                return False
            if previous and oldrep:
                logger.info(f"we will do a diff - previous and oldrep exist, scan id {self.scanid}, previous is no longer last")
                previous.is_last = False
                previous.save()
                created_rep.prev_rep = previous.id    
                created_rep.save()
                diff_stat = self.diff_input(newrep, oldrep, created_rep, previous)
                if diff_stat:
                    logger.info(f"wow, much success: diff_input passed for scan id {self.scanid}")
            else:
                logger.info(f"no prev rep, so just the inserts please, still no issue for scan id {self.scanid}")
                
        else:
            logger.info(f"new rep was not parsed, was saved as failed, main_input not called, scan id {self.scanid}")
            if previous:
                created_rep.prev_rep = previous.id    
                created_rep.save()
            return False
        return True
    
    def get_prev_rep(self):
        previous = 0
        oldrep = 0
        #Find if standard report for this scan exists
        try:
            standard_report = reports.objects.get(scan=self.scanid, standard=True)
        except Exception as e:
            logger.warning(f"Could not find standard report for scan {self.scanid}, proceeding with last. Django error: {e}")
            standard_report = 0
        try:
            if standard_report:
                previous = standard_report
            else:
                previous = reports.objects.filter(scan=self.scanid, is_last=True)[0]
            try:
                oldrep = NmapParser.parse_fromfile(previous.path_to)
            except Exception as e:
                logger.exception(f"could not parse previous from file, NmapParser error: {e}")
                oldrep = 0
        except Exception as e:
            logger.exception(f"Could not find previous or standard report, Django error: {e}")
            previous = 0
        logger.info(f"previous report for scan {self.scanid} is {previous} and oldrep is {oldrep}")
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
        except Exception as e:
            logger.exception(f"necessary objects - resourcegroup rgroup or scan {self.scanid} - not found: {e}")
            status = False
        try:
            newrep = NmapParser.parse_fromstring(xml_result)
        except Exception as e:
            logger.exception(f"could not parse new report from string: {e}")
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
            except Exception as e:
                logger.exception(f"parsing or report insert of {newrep.summary} failed, Django error: {e}")
                status = False
        failed_rep = reports.objects.create(
                            summary = "Report parsing failed",
                            path_to = filepath,
                            is_last = False,
                            parse_success = status
        )
        logger.warning(f"parsing or report insert of {newrep.summary} failed, inserted failed rep instead")
        return (failed_rep, newrep)
    
    def main_input(self, newrep, created_rep):
        try:
            logger.info(f"starting to iterate over hosts in new report for scan {self.scanid}")
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
                try:
                    
                    host_obj, host_created = hosts.objects.update_or_create(main_address=ahost.address, defaults=defaults_hosts)
                except Exception as e:
                    logger.exception(f"could not insert ({host_created}) or update host {ahost.address} in hosts table, Django error: {e}")
                logger.info(f"inserted or updated {host_created} host: {host_obj}")
                try:
                    created_rep.hosts_set.add(host_obj)
                except Exception as e:
                    logger.exception(f"could not add host {host_obj} to report {created_rep}, Django error: {e}")
                logger.info(f"added host {host_obj} to report {created_rep}, starting to iterate over services")
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
                    logger.info(f"inserted or updated ({serv_created}) service: {serv_obj}")
                    try:
                        host_obj.services_set.add(serv_obj)
                        created_rep.services_set.add(serv_obj)
                    except Exception as e:
                        logger.exception(f"could not add service {serv_obj} to host {host_obj} or report {created_rep}, Django error: {e}")
        except Exception as e:
            logger.exception(f"Something failed in main_input: {e}")
            return False            
        return True
    
    def nested_obj(self, objname):
        rval = None
        splitted = objname.split("::")
        if len(splitted) == 2:
            rval = splitted
        return rval
    
    def diff_input(self, newrep, oldrep, created_rep, previous):
        logger.info(f"here i will do the diff - starting diff_input for scan {self.scanid}. REPORT LEVEL: {newrep.summary}, {oldrep.summary}")
        rep_ndiff = newrep.diff(oldrep)
        logger.info(f"REPORT LEVEL diff output: {rep_ndiff}")
        logger.info(f"REPORT LEVEL diff changes TO ITERATE OVER: {rep_ndiff.changed()}")
        for attr in rep_ndiff.changed():
            if "::" not in attr:
                try:
                    attr_change = changes.objects.create(
                        attribute = attr,
                        cur_val = str(getattr(newrep, attr)),
                        prev_val = str(getattr(oldrep, attr)),
                        status = "CHANGED",
                        cur_report = created_rep,
                        prev_rep = previous.id
                    )
                except Exception as e:
                    logger.exception(f"could not create change object for diff report lvl change {attr}. TRYING TO CONTINUE ANYWAY. Django error: {e}")
                    continue
                logger.info(f"successfully created change object {attr_change} for diff report lvl change {attr}")
            else:
                logger.info(f"this never happens? - going one level deeper, from report to host level on change {attr}")
                nested = self.nested_obj(attr)
                if nested is not None:
                    if nested[0] == "NmapHost":
                        curhost = newrep.get_host_byid(nested[1])
                        prevhost = oldrep.get_host_byid(nested[1])
                        host_diff = curhost.diff(prevhost)
                        
                        #added services
                        logger.info(f"STARTING TO ITERATE OVER HOST LEVEL ({curhost}) diff ADDED changes: SERVICE LEVEL")
                        for addserv in host_diff.added():
                            nestserv = self.nested_obj(addserv)
                            if nestserv is not None:
                                if nestserv[0] == "NmapService":
                                    #add service to db
                                    aservice = curhost.get_service_byid(nestserv[1])
                                    try:
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
                                    except Exception as e:
                                        logger.exception(f"could not retrieve or create objects while adding service {aservice} on host {curhost.address} for diff service lvl change {attr}. TRYING TO CONTINUE ANYWAY. Django error: {e}")
                                        continue
                                    logger.info(f"successfully added service {servadr} to services and change {serv_in_changes} to changes")
                            else:
                                logger.warning(f"This should never happen - Was not expecting an attribute when parsing host diff ADDED SERVICES {attr}")
                        logger.info(f"STARTING TO ITERATE OVER HOST LEVEL ({curhost}) diff REMOVED changes: SERVICE LEVEL")
                        for remserv in host_diff.removed():
                            nestserv = self.nested_obj(remserv)
                            if nestserv is not None:
                                if nestserv[0] == "NmapService":
                                    #add service to db
                                    rservice = prevhost.get_service_byid(nestserv[1])
                                    try:
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
                                    except Exception as e:
                                        logger.exception(f"could not retrieve or create objects while removing service {rservice} on host {curhost.address} for diff service lvl change {attr}. TRYING TO CONTINUE ANYWAY. Django error: {e}")
                                        continue
                                    logger.info(f"successfully inserted removed service {servrem} to services and change {remserv_in_changes} to changes")
                            else:
                                logger.warning(f"This should never happen - Was not expecting an attribute when parsing host diff REMOVED SERVICES {attr}")
                        logger.info(f"STARTING TO ITERATE OVER HOST LEVEL ({curhost}) diff CHANGED changes: SERVICE LEVEL")
                        for chserv in host_diff.changed():
                            nestedhost = self.nested_obj(chserv)
                            if nestedhost is not None:
                                if nestedhost[0] == "NmapService":
                                    #for every changed service
                                    cservice = curhost.get_service_byid(nestedhost[1])
                                    pservice = prevhost.get_service_byid(nestedhost[1])
                                    serv_diff = cservice.diff(pservice)
                                    logger.info(f"STARTING TO ITERATE OVER SERVICE LEVEL ({cservice}) diff CHANGED changes: SERVICE TO SERVICE LEVEL")
                                    for servattr in serv_diff.changed():
                                        nestedserv = self.nested_obj(servattr)
                                        if nestedserv is not None:
                                            logger.warning(f"WTF? - here in service to service changes - {servattr} - no more nesting should be possible.")
                                        else:
                                            try:
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
                                            except Exception as e:
                                                logger.exception(f"could not retrieve or create objects while inserting changes for service {cservice} on host {curhost.address}. TRYING TO CONTINUE ANYWAY. Django error: {e}")
                                                continue
                                            logger.info(f"successfully inserted changed service {servattrch} to changes")
                                    logger.warning(f"THE FOLLOWING MIGHT NOT BE IMPLEMENTED YET, or is inserted as ADDED under service changes for {cservice} on host {curhost.address}")
                                    for addattr in serv_diff.added():
                                        logger.warning(f"Added under service changes: {addattr}")

                                    logger.warning(f"THE FOLLOWING MIGHT NOT BE IMPLEMENTED YET, or is inserted as REMOVED under service changes for {cservice} on host {curhost.address}")
                                    for remattr in serv_diff.removed():
                                        logger.warning(f"Removed under service changes: {remattr}")

                            else:
                                try:
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
                                except Exception as e:
                                    logger.exception(f"could not retrieve or create objects while inserting SERVICE changes for host {curhost.address}. TRYING TO CONTINUE ANYWAY. Django error: {e}")
                                    continue
                                logger.info(f"successfully inserted into changes {chservch} some value for host {curhost.address}")
        
        logger.info("STARTING TO ITERATE OVER HOST LEVEL diff hosts ADDED changes: HOST LEVEL")
        for add in rep_ndiff.added():
            nested = self.nested_obj(add)
            if nested is not None:
                if nested[0] == "NmapHost":
                    ahost = newrep.get_host_byid(nested[1])
                    try:
                        dbhost_a = hosts.objects.get(main_address=ahost.address)
                        hadr = hosts_added_removed.objects.create(
                            cur_report=created_rep,
                            host=dbhost_a,
                            prev_report=previous,
                            status="ADDED"
                        )
                    except Exception as e:
                        logger.exception(f"could not retrieve or create objects while inserting ADDED host {ahost.address} to hosts_added_removed for diff host lvl change {add}. TRYING TO CONTINUE ANYWAY. Django error: {e}")
                        continue
                    logger.info(f"successfully inserted added host {ahost.address} to hosts_added_removed")
                    
                    try:
                        hadr_ch = changes.objects.create(
                            cur_report=created_rep,
                            host=dbhost_a,
                            prev_rep=previous.id,
                            status="ADDED"
                        )
                    except Exception as e:
                        logger.exception(f"could not retrieve or create objects while inserting ADDED host {ahost.address} to CHANGED for diff host lvl change {add}. TRYING TO CONTINUE ANYWAY. Django error: {e}")
                        continue
                    logger.info(f"successfully inserted added host {ahost.address} to changes")
                    logger.info("STARTING TO ITERATE OVER SERVICE LEVEL diff services ADDED changes: SERVICE LEVEL")
                    for aserv in ahost.services:
                        try:
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
                        except Exception as e:
                            logger.exception(f"could not retrieve or create objects while inserting ADDED service {aserv} to services_added_removed or changed for diff host lvl change {add}. TRYING TO CONTINUE ANYWAY. Django error: {e}")
                            continue
                        logger.info(f"successfully inserted added service {aserv} to services_added_removed and changes")
                    
        logger.info("STARTING TO ITERATE OVER HOST LEVEL diff hosts REMOVED changes: HOST LEVEL")
        for rem in rep_ndiff.removed():
            nested = self.nested_obj(rem)
            if nested is not None:
                if nested[0] == "NmapHost":
                    rhost = oldrep.get_host_byid(nested[1])
                    try:
                        dbhost_r = hosts.objects.get(main_address=rhost.address)
                        hadrgone = hosts_added_removed.objects.create(
                            cur_report=created_rep,
                            host=dbhost_r,
                            prev_report=previous,
                            status="REMOVED"
                        )
                        hadrgone_ch = changes.objects.create(
                            cur_report=created_rep,
                            host=dbhost_r,
                            prev_rep=previous.id,
                            status="REMOVED"
                        )
                    except Exception as e:
                        logger.exception(f"could not retrieve or create objects while inserting REMOVED host {rhost.address} to hosts_added_removed or changes for diff host lvl change {rem}. TRYING TO CONTINUE ANYWAY. Django error: {e}")
                        continue
                    logger.info(f"successfully inserted removed host {rhost.address} to hosts_added_removed and changes")
                    logger.info("STARTING TO ITERATE OVER SERVICE LEVEL diff services REMOVED changes: SERVICE LEVEL")
                    for rserv in rhost.services:
                        try:
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
                        except Exception as e:
                            logger.exception(f"could not retrieve or create objects while inserting REMOVED service {rserv} to services_added_removed or changes for diff host lvl change {rem}. TRYING TO CONTINUE ANYWAY. Django error: {e}")
                            continue
                        logger.info(f"successfully inserted removed service {rserv} to services_added_removed and changes")
        logger.info(f"Did not fail on the diff parse, wow, or at least got to the end of it, previous report was: {previous}, new rep - {created_rep}")
        return True
    
    def scan_call(self):
        logger.info(f"Scanning {self.scan.get_target()}, with options {self.scan.ScanTemplate}")
        
        # Do the scan here
        
        #Start the scan
        nmap_proc = NmapProcess(targets=self.scan.get_target(), options=self.scan.ScanTemplate, safe_mode=False)
        nmap_proc.run_background()
        logger.info(f"Scan {self.scanid} started")
        
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
        
        logger.info(f"Scan {self.scanid} finished")
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
            logger.warning(f"Scan {self.scanid} failed")
        self.scan.save()
        logger.info(f"Scan {self.scanid} parameters updated")
        
        ct_date = datetime.strftime(timezone.now(), '%Y_%m_%d_%H_%M_%s')
        # Save the logs in a file
        log_result = nmap_proc.stderr
        logname = f"log_{self.scan.scanName}_{ct_date}.log"
        log_path = self.save_nmap_report_or_log(log_result, logname, "log")
        
        logger.info(f"Scan {self.scanid} NMAP logs saved to {log_path}")
        
        # Save the report in a file
        xml_result = nmap_proc.stdout
        filename = f"scan_{self.scan.scanName}_{ct_date}.xml"
        report_path = self.save_nmap_report_or_log(xml_result, filename, "report")
        if report_path:
            logger.info(f"Report saved to {report_path}")
            self.xml_result = xml_result
            self.report_path = report_path            
            return True
        else:
            logger.error(f"Failed to save report to {report_path}")
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
        except Exception as e:
            logger.exception(f"Failed to create report or log file: {e}")
            return False