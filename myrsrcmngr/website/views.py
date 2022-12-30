from django.shortcuts import get_object_or_404, render
from django.views import View
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.http import JsonResponse
from django.contrib.humanize.templatetags.humanize import naturaltime
from .serializers import ScansSerializer, ReportsSerializer, ResourcegroupsSerializer, HostsSerializer, ServicesSerializer
from rest_framework.decorators import api_view
from .owner import OwnerCreateView, OwnerUpdateView, OwnerDeleteView, GroupOwnerCreateView, GroupOwnerUpdateView, GroupOwnerDeleteView, HostOwnerUpdateView
from django.urls import reverse
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseNotAllowed
import os
import random
from django.db.models import Q
from django.utils import timezone
import logging



# Create your views here.
from .models import scans, hosts, reports, resourcegroups, services, changes
logger = logging.getLogger(__name__)

def index(request):
    con = {}
    rreport = None
    for rgroup in resourcegroups.objects.all().order_by('-updated_at')[:5]:
        
        try:
            rreport = rgroup.reports_set.latest('id')
            groupname = rgroup.name
            con[groupname] = rreport
        except:
            rreport = None
    context = {
        'con': con
    }
    return render(request, 'index.html', context)

def dashboard_changes_table(request):
    if request.method == 'GET':
        eachchanges = {}
        allchanges = []
        mainchanges = {'total': 0,
                        'changes': [{
                                    'main_address':'',
                                    'group_name':'',
                                    'group_id':0,
                                    'host_id':0,
                                    'report_date':'',
                                    'report_id':0,
                                    'attribute': '',
                                    'new_value': '',
                                    },
                                ]
                    }        
        #In order to relieve some data amount concerns, select just the last 100 successful reports
        reports_list = reports.objects.all().filter(parse_success=True).order_by('-id')[:100]

        #for each report, find the notable changes (status, state, os_fingerprint) that have not been dismissed, and are not the elapsed time
        #Further filter down for those changes that have host indicated
        filteredChanges = changes.objects.filter(cur_report__in=reports_list)
        filteredChanges = filteredChanges.exclude(dismissed=True).exclude(attribute='elapsed').exclude(host=None)
        filteredChanges = filteredChanges.filter(Q(attribute='status') | Q(attribute='state') | Q(attribute='os_fingerprint'))
        for change in filteredChanges:
            host = change.host
            group = host.resourcegroup
            eachchanges['main_address'] = host.main_address
            eachchanges['group_name'] = group.name
            eachchanges['group_id'] = group.id
            eachchanges['host_id'] = host.id
            eachchanges['report_date'] = change.cur_report.f_endtime_str()
            eachchanges['report_id'] = change.cur_report.id
            eachchanges['attribute'] = change.attribute
            if change.attribute == 'state' and change.cur_val == 'open':
                eachchanges['new_value'] = change.service.name_conc
            elif change.attribute == 'state':
                eachchanges = {}
                continue
            else:
                eachchanges['new_value'] = change.cur_val
            allchanges.append(eachchanges)
            eachchanges = {}
        mainchanges['total'] = len(allchanges)
        mainchanges['changes'] = allchanges
        return render(request, 'selected_changes.html', {'changes':mainchanges})

@api_view(['POST'])
def dashboard_dismiss(request):
    if request.method == 'POST':
        # get the last 100 reports
        last_100_reports = reports.objects.all().order_by('-id')[:100]
        # get all changes that relate to the last 100 reports
        filteredchanges = changes.objects.filter(cur_report__in=last_100_reports)
        # set the 'dismissed' attribute to True for all changes
        filteredchanges.update(dismissed=True)
        # return a JSON response indicating that the changes have been dismissed
        return JsonResponse({'dismissed': True})

@api_view(['GET'])
def dashboard_changes(request):
    if request.method == 'GET':
        eachchanges = {}
        allchanges = []
        mainchanges = {'total': 0,
                        'changes': [{
                                    'main_address':'',
                                    'group_name':'',
                                    'group_id':0,
                                    'host_id':0,
                                    'report_date':'',
                                    'report_id':0,
                                    'attribute': '',
                                    'new_value': '',
                                    },
                                ]
                    }        
        #In order to relieve some data amount concerns, select just the last 100 successful reports
        reports_list = reports.objects.all().filter(parse_success=True).order_by('-id')[:100]

        #for each report, find the notable changes (status, state, os_fingerprint) that have not been dismissed, and are not the elapsed time
        #Further filter down for those changes that have host indicated
        filteredChanges = changes.objects.filter(cur_report__in=reports_list)
        filteredChanges = filteredChanges.exclude(dismissed=True).exclude(attribute='elapsed').exclude(host=None)
        filteredChanges = filteredChanges.filter(Q(attribute='status') | Q(attribute='state') | Q(attribute='os_fingerprint'))
        for change in filteredChanges:
            host = change.host
            group = host.resourcegroup
            eachchanges['main_address'] = host.main_address
            eachchanges['group_name'] = group.name
            eachchanges['group_id'] = group.id
            eachchanges['host_id'] = host.id
            eachchanges['report_date'] = change.cur_report.f_endtime_str()
            eachchanges['report_id'] = change.cur_report.id
            eachchanges['attribute'] = change.attribute
            if change.attribute == 'state' and change.cur_val == 'open':
                eachchanges['new_value'] = change.service.name_conc
            elif change.attribute == 'state':
                eachchanges = {}
                continue
            else:
                eachchanges['new_value'] = change.cur_val
            allchanges.append(eachchanges)
            eachchanges = {}
        mainchanges['total'] = len(allchanges)
        mainchanges['changes'] = allchanges
        return JsonResponse({"data":mainchanges})


def dashboard(request):
    con = {}
    rreport = None
    report_changes = {}
    for rgroup in resourcegroups.objects.all().order_by('-updated_at'):
        
        try:
            rreport = rgroup.reports_set.latest('id')
            groupname = rgroup.name
            rchanges = rreport.changes_set.all().exclude(attribute='elapsed')
            changes_count = rchanges.count()
            if rchanges:
                report_changes['hosts_changed'] = 0
                report_changes['hosts_added'] = 0
                report_changes['hosts_removed'] = 0
                report_changes['services_changed'] = 0
                report_changes['services_added'] = 0
                report_changes['services_removed'] = 0
                report_changes['hosts_up'] = None
                report_changes['hosts_down'] = None
                report_changes['hosts_total'] = None
                counter = 0
                for change in rchanges:
                    counter = counter + 1
                    if change.attribute == 'hosts_up':
                        print('hosts_up', change.cur_val, change.prev_val)
                        if change.prev_val is None:
                            change.prev_val = 0
                        report_changes['hosts_up'] = int(change.cur_val) - int(change.prev_val)
                    elif change.attribute == 'hosts_down':
                        if change.prev_val is None:
                            change.prev_val = 0
                        report_changes['hosts_down'] = int(change.cur_val) - int(change.prev_val)
                    elif change.attribute == 'hosts_total':
                        if change.prev_val is None:
                            change.prev_val = 0
                        report_changes['hosts_total'] = int(change.cur_val) - int(change.prev_val)
                    elif change.status == 'CHANGED' and change.host is not None and change.service is None:
                        report_changes['hosts_changed'] = report_changes['hosts_changed'] + 1
                    elif change.status == 'ADDED' and change.host is not None and change.service is not None:
                        report_changes['services_added'] = report_changes['services_added'] + 1
                    elif change.status == 'CHANGED' and change.host is not None and change.service is not None:
                        report_changes['services_changed'] = report_changes['services_changed'] + 1
                    elif change.status == 'REMOVED' and change.host is not None and change.service is not None:
                        report_changes['services_removed'] = report_changes['services_removed'] + 1
                    elif change.status == 'REMOVED' and change.host is not None and change.service is None:
                        report_changes['hosts_removed'] = report_changes['hosts_removed'] + 1
                    elif change.status == 'ADDED' and change.host is not None and change.service is None:
                        report_changes['hosts_added'] = report_changes['hosts_added'] + 1
            con[groupname] = {
                'report':rreport,
                'report_changes': report_changes,
                'changes':rchanges,
                'changes_count':changes_count,
            }
        except:
            rreport = None
    context = {
        'con': con
    }
    
    eachchanges = {}
    allchanges = []
    mainchanges = {'total': 0,
                    'changes': [{
                                'main_address':'',
                                'group_name':'',
                                'group_id':0,
                                'host_id':0,
                                'report_date':'',
                                'report_id':0,
                                'attribute': '',
                                'new_value': '',
                                },
                            ]
                }        
    #In order to relieve some data amount concerns, select just the last 100 successful reports
    reports_list = reports.objects.all().filter(parse_success=True).order_by('-id')[:100]

    #for each report, find the notable changes (status, state, os_fingerprint) that have not been dismissed, and are not the elapsed time
    #Further filter down for those changes that have host indicated
    filteredChanges = changes.objects.filter(cur_report__in=reports_list)
    filteredChanges = filteredChanges.exclude(dismissed=True).exclude(attribute='elapsed').exclude(host=None)
    filteredChanges = filteredChanges.filter(Q(attribute='status') | Q(attribute='state') | Q(attribute='os_fingerprint'))
    for change in filteredChanges:
        host = change.host
        group = host.resourcegroup
        eachchanges['main_address'] = host.main_address
        eachchanges['group_name'] = group.name
        eachchanges['group_id'] = group.id
        eachchanges['host_id'] = host.id
        eachchanges['report_date'] = change.cur_report.f_endtime_str()
        eachchanges['report_id'] = change.cur_report.id
        eachchanges['attribute'] = change.attribute
        if change.attribute == 'state' and change.cur_val == 'open':
            eachchanges['new_value'] = change.service.name_conc
        elif change.attribute == 'state':
            eachchanges = {}
            continue
        else:
            eachchanges['new_value'] = change.cur_val
        allchanges.append(eachchanges)
        eachchanges = {}
    mainchanges['total'] = len(allchanges)
    mainchanges['changes'] = allchanges
    context['changes'] = mainchanges
    
    activescans = scans.objects.all().filter(active=True)[:5]
    context['activescans'] = activescans
    
    return render(request, 'index.html', context)

#CRUD views for Scans

class ScanCreateView(OwnerCreateView):
    model = scans
    fields = ['resourcegroup', 'scanName', 'ScanTemplate', 'ScanSchedule']
    # By convention:
    # template_name = "website/scans_form.html"

class ScanUpdateView(OwnerUpdateView):
    model = scans
    fields = ['resourcegroup', 'scanName', 'ScanTemplate', 'ScanSchedule']
    # By convention:
    # template_name = "website/scans_form.html"

class ScanDeleteView(OwnerDeleteView):
    model = scans
    fields = ['resourcegroup', 'scanName', 'ScanTemplate', 'ScanSchedule', 'active']
    # By convention:
    # template_name = "website/scans_confirm_delete.html"
    
class ScansListView(ListView):
    model = scans
    ordering = ['next_execution_at']
    # By convention:
    # template_name = "website/scans_list.html"
    
@api_view(['POST', 'GET'])
def scan_toggle(request, pk):
    if request.method == 'POST':
        active = request.POST.get('active')
        active_scan = get_object_or_404(scans, pk=pk)
        if active:
            #Get all scans belonging to the same resource group that have active set to 1 and are not the current scan
            other_active_scans = scans.objects.filter(resourcegroup=active_scan.resourcegroup).exclude(active=False).exclude(id=active_scan.id)
        
            #Change all other active scans to False
            for other_active_scan in other_active_scans:
                other_active_scan.active = False
                other_active_scan.save()
        active_scan.active = active
        active_scan.next_execution_at = timezone.now()
        active_scan.save()
        return JsonResponse({"active":active})

@api_view(['GET'])
def scan_refresh(request, pk):
    if request.method == 'GET':
        scan = scans.objects.get(pk=pk)
        if scan:
            scanreports = scan.reports_set.all()
            if scanreports:
                serializer = ReportsSerializer(scanreports, many=True)
                scanreports = serializer.data
        else:
            scanreports = None
        return JsonResponse({"data":scanreports})

@api_view(['GET'])
def scanlist_refresh(request):
    if request.method == 'GET':
        allscans = scans.objects.all()
        if allscans:
            serializer = ScansSerializer(allscans, many=True)
            allscans = serializer.data
        else:
            allscans = None
        return JsonResponse({"data":allscans})

@api_view(['GET'])
def grouplist_refresh(request):
    if request.method == 'GET':
        allgroups = resourcegroups.objects.all()
        if allgroups:
            serializer = ResourcegroupsSerializer(allgroups, many=True)
            allgroups = serializer.data
        else:
            allgroups = None
        return JsonResponse({"data":allgroups})

@api_view(['GET'])
def scans_group_refresh(request, pk):
    if request.method == 'GET':
        group = resourcegroups.objects.get(pk=pk)
        if group:
            scans = group.scans_set.all()
            if scans:
                serializer = ScansSerializer(scans, many=True)
                scans = serializer.data
        else:
            scans = None
        return JsonResponse({"data":scans})


@api_view(['GET'])
def scanlist_totals_refresh(request):
    if request.method == 'GET':
        totals = {
            'scans_created_total': 0,
            'scans_active_total': 0,
            'scans_running_total': 0,
        }
        created_total = scans.objects.count()
        if created_total > 0:
            totals['scans_created_total'] = created_total
        active_total = scans.objects.filter(active=True).count()
        if active_total > 0:
            totals['scans_active_total'] = active_total
        running_total = scans.objects.filter(active=True, status=2).count()
        if running_total > 0:
            totals['scans_running_total'] = running_total
        return JsonResponse({"data":totals})

@api_view(['GET'])
def grouplist_totals_refresh(request):
    if request.method == 'GET':
        totals = {
            'groups_created_total': 0,
            'groups_scans_total': 0,
            'groups_hosts_total': 0,
        }
        created_total = resourcegroups.objects.count()
        if created_total > 0:
            totals['groups_created_total'] = created_total
        scans_total = 0
        hosts_total = 0
        for group in resourcegroups.objects.all():
            scans_total = scans_total + group.scans_set.count()
            hosts_total = hosts_total + group.hosts_set.count()
        totals['groups_scans_total'] = scans_total
        totals['groups_hosts_total'] = hosts_total
        return JsonResponse({"data":totals})

@api_view(['GET'])
def group_changes_refresh(request, pk):
    if request.method == 'GET':
        totals = {
                'scans_count': 0,
                'hosts_count': 0,
                'active_scans_count': 0,
                'running_scans_count': 0,
                'hostsup_count': 0,
                'hostsdown_count': 0,
        }
        group = resourcegroups.objects.get(pk=pk)
        if group:
            totals['scans_count'] = group.scans_count()
            totals['hosts_count'] = group.hosts_count()
            totals['active_scans_count'] = group.active_scans_count()
            totals['running_scans_count'] = group.running_scans_count()
            totals['hostsup_count'] = group.hostsup_count()
            totals['hostsdown_count'] = group.hostsdown_count()
        return JsonResponse({"data":totals})
    
@api_view(['GET'])
def hostsgroup_refresh(request, pk):
    if request.method == 'GET':
        group = resourcegroups.objects.get(pk=pk)
        if group:
            hosts = group.hosts_set.all()
            if hosts:
                serializer = HostsSerializer(hosts, many=True)
                hosts = serializer.data
        else:
            hosts = None
        return JsonResponse({"data":hosts})
    
@api_view(['GET'])
def scans_list(request):
    if request.method == 'GET':
        allscans = scans.objects.all()
        serializer = ScansSerializer(allscans, many=True)
        return JsonResponse({"scans":serializer.data})

@api_view(['GET'])
def scan_progress(request):
    if request.method == 'GET':
        active_scan = scans.objects.all()
        if active_scan:
            
            serializer = ScansSerializer(active_scan, many=True)
            return JsonResponse({"scans":serializer.data})       

class ScanProgressView(View):
    
    def get(self, request, pk):
        try:
            mainscan = scans.objects.get(pk=pk)
        except:
            mainscan = None
        scanreturn = {}
        if mainscan:
            #stats
            #Number of reports generated by the scan
            scanreports = mainscan.reports_set.all()
            scanrepcount = scanreports.count()
            summed_duration = 0
            for rep in scanreports:
                summed_duration = summed_duration + rep.elapsed
            if scanrepcount > 0:            
                scanreturn['average_duration'] = summed_duration / scanrepcount
            else:
                scanreturn['average_duration'] = 0
            scanreturn['num_reports'] = scanrepcount
            #statuses
            scanreturn['scan'] = 1
            scanreturn['scan_status'] = mainscan.formatted_status()
            #info
            scanreturn['last_executed'] = mainscan.formatted_last_executed()
            if mainscan.active:
                scanreturn['active'] = 'ON'
                scanreturn['next_at'] = naturaltime(mainscan.next_execution_at)
                if mainscan.status == 2:
                    scanreturn['status'] = mainscan.task_status
                    scanreturn['name'] = mainscan.task_name
                    scanreturn['etc'] = mainscan.task_etc
                    scanreturn['progress'] = mainscan.task_progress
            else:
                scanreturn['active'] = 'OFF'
        else:
            scanreturn['scan'] = 0
        
        return JsonResponse(scanreturn, safe=False)
        
        
class ScanDetailView(DetailView):
    model = scans
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the default context data
        context = super().get_context_data(**kwargs)

        # Add additional querysets or dictionaries to the context
        context['reports'] = self.object.reports_set.order_by('id')
        return context
#CRUD views for Hosts

class HostCreateView(OwnerCreateView):
    model = hosts
    # By convention:
    # template_name = "website/hosts_form.html"

class HostUpdateView(HostOwnerUpdateView):
    model = hosts
    fields = ['name', 'description']
    # By convention:
    # template_name = "website/scans_form.html"

class HostDeleteView(OwnerDeleteView):
    model = hosts
    # By convention:
    # template_name = "website/scans_confirm_delete.html"
    
class HostsListView(ListView):
    model = hosts
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the default context data
        context = super().get_context_data(**kwargs)
        totals = {
            'total_hosts': hosts.objects.all().filter(is_removed=None).count(),
            'total_hosts_up': hosts.objects.all().filter(status="up").count(),
            'total_hosts_down': hosts.objects.all().filter(status="down").count(),
        }
        context['totals'] = totals
        return context
    # By convention:
    # template_name = "website/scans_list.html"

class HostDetailView(DetailView):
    model = hosts
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the default context data
        context = super().get_context_data(**kwargs)
        totals = {
                    'num_of_services': self.object.num_of_services(),
                    'num_open_ports': self.object.num_open_ports(),
                    'str_open_ports': self.object.str_open_ports(),
            }
        context['totals'] = totals
        context['changes'] = self.object.changes_set.order_by('-id')
        context['services'] = self.object.services_set.exclude(state__contains='closed').order_by('-id')
        return context

@api_view(['GET'])
def host_changes_refresh(request, pk):
    if request.method == 'GET':
        host = hosts.objects.get(pk=pk)
        totals = None
        if host: 
            totals = {
                    'num_of_services': host.num_of_services(),
                    'num_open_ports': host.num_open_ports(),
                    'str_open_ports': host.str_open_ports(),
            }
        return JsonResponse({"data":totals}) 
    
@api_view(['GET'])
def host_services_refresh(request, pk):
    if request.method == 'GET':
        host = hosts.objects.get(pk=pk)
        if host:
            services = host.services_set.all()
            if services:
                serializer = ServicesSerializer(services, many=True)
                services = serializer.data
        else:
            services = None
        return JsonResponse({"data":services})

@api_view(['GET'])
def hosts_totals_refresh(request):
    if request.method == 'GET':
        totals = {
            'total_hosts': hosts.objects.all().filter(is_removed=None).count(),
            'total_hosts_up': hosts.objects.all().filter(status="up").count(),
            'total_hosts_down': hosts.objects.all().filter(status="down").count(),
        }
        return JsonResponse({"data":totals})

@api_view(['GET'])
def hosts_refresh(request):
    if request.method == 'GET':
        allhosts = hosts.objects.all()
        if allhosts:
            serializer = HostsSerializer(allhosts, many=True)
            allhosts = serializer.data
        else:
            allhosts = None
        return JsonResponse({"data":allhosts})


#CRUD views for Groups

class ResourcegroupCreateView(GroupOwnerCreateView):
    model = resourcegroups
    fields = ['name','description', 'subnet']
    # By convention:
    # template_name = "website/hosts_form.html"

class ResourcegroupUpdateView(GroupOwnerUpdateView):
    model = resourcegroups
    fields = ['name','description', 'subnet']
    # By convention:
    # template_name = "website/scans_form.html"

class ResourcegroupDeleteView(GroupOwnerDeleteView):
    model = resourcegroups
    # By convention:
    # template_name = "website/resourcegroups_confirm_delete.html"
    
class ResourcegroupsListView(ListView):
    model = resourcegroups
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the default context data
        context = super().get_context_data(**kwargs)
        groups = resourcegroups.objects.all()
        group_data = []
        for group in groups:
            if group.hosts_count() > 0:
                group_data.append({
                    'label': group.name,
                    'value': group.hosts_count()
                })
        context['groups'] = group_data
        return context
    # By convention:
    # template_name = "website/scans_list.html"

class ResourcegroupDetailView(DetailView):
    model = resourcegroups
    template_name = "website/resourcegroup_detail.html"

# List and Detail view for Reports

class ReportsListView(ListView):
    model = reports
    
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the default context data
        context = super().get_context_data(**kwargs)
        totals = {
                'total_reports': reports.objects.all().count(),
                'total_success_reports': reports.objects.all().filter(parse_success=True).count(),
                'total_failed_reports': reports.objects.all().filter(parse_success=False).count(),
            }
        context['totals'] = totals
        return context
    
    # By convention:
    # template_name = "website/scans_list.html"

def download_report(request, pk):
    # Get the report object with the given primary key
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET'])
    report = get_object_or_404(reports, pk=pk)

    # Check if the report has a file associated with it
    if not report.path_to:
        # If not, return a 404 error
        return HttpResponseNotFound("No file associated with this report")

    # Get the file path for the report's file
    file_path = report.path_to

    # Check if the file exists
    if not os.path.exists(file_path):
        # If not, return a 404 error
        return HttpResponseNotFound("File not found")

    # Open the file in binary mode
    with open(file_path, 'rb') as f:
        # Create a Django response object with the file's contents
        response = HttpResponse(f.read(), content_type="application/xml")
        # Set the response's content-disposition header to tell the browser to download the file
        response['Content-Disposition'] = f'attachment; filename="{report.download_name()}.xml"'
        # Return the response
        return response


class ReportDetailView(DetailView):
    model = reports
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the default context data
        context = super().get_context_data(**kwargs)

        # Add additional querysets or dictionaries to the context
        changed_hosts = []

        allhosts = hosts.objects.filter(reports_belonging_to=self.object.id)
        allchanges = self.object.changes_set.all().exclude(attribute='elapsed').exclude(host=None)
        for onehost in allhosts:
            one_row = {'main_address':'',
                        'status':'',
                        'hostnames':'',
                        'os_fingerprint':'',
                        'cur_open_ports_nr':0,
                        'cur_open_ports':'',
                        'open_ports_nr':0,
                        'open_ports':'',
                        'change':'',
                        'other_host_changes':0,
                        'other_service_changes':0,
                        'plusorminus':0,
                        'id':0,
                        }
            #host specific changes
            for change in allchanges.filter(host=onehost, service=None):
                one_row['id'] = change.host.id
                one_row['main_address'] = change.host.main_address
                one_row['change'] = change.status
                if change.attribute == 'status':
                    one_row['status'] = change.cur_val
                    
                elif change.attribute == 'os_fingerprint':
                    one_row['os_fingerprint'] = change.cur_val
                
                elif change.attribute == 'hostnames':
                    one_row['hostnames'] = change.cur_val
                else:
                    one_row['other_host_changes'] += 1
           
            #service specific changes
            open_ports = []
            for change in allchanges.filter(host=onehost).exclude(service=None):
                one_row['id'] = change.host.id
                one_row['main_address'] = change.host.main_address
                if change.attribute == 'state' and change.cur_val == 'open':
                    one_row['open_ports_nr'] += 1
                    open_ports.append(change.cur_val)
                elif change.attribute == 'state' and change.cur_val == 'closed' and change.prev_val == 'open':
                    one_row['open_ports_nr'] -= 1
                elif change.attribute == 'state' and change.cur_val == 'filtered' and change.prev_val == 'open':
                    one_row['open_ports_nr'] -= 1
                else:
                    one_row['other_service_changes'] += 1
                    
            one_row['open_ports'] = ', '.join(open_ports)
            one_row['cur_open_ports'] = onehost.str_open_ports()
            one_row['cur_open_ports_nr'] = onehost.num_open_ports()
            if one_row['open_ports_nr'] > 0:
                one_row['plusorminus'] = True
            else:
                one_row['plusorminus'] = False
            if one_row['id'] != 0:
                changed_hosts.append(one_row)
        
        context['hosts'] = changed_hosts
        context['changes'] = self.object.changes_set.order_by('-id')
        context['download_url'] = reverse('website:download_report', args=[self.object.id])
        return context
    
@api_view(['POST', 'GET'])
def set_standard_report(request, pk):
    if request.method == 'POST':
        standard = request.POST.get('standard')
        report = get_object_or_404(reports, pk=pk)
        if standard:
            #Get all reports belonging to the same scan that have standard set to 1 and are not the current report
            other_standard_reports = reports.objects.filter(scan=report.scan).exclude(standard=0).exclude(id=report.id)
        
            #Change all other standard reports to 0
            for other_standard_report in other_standard_reports:
                other_standard_report.standard = 0
                other_standard_report.save()
        
        #Set the current report to standard
        report.standard = standard
        report.save()
        return JsonResponse({"standard":standard})

@api_view(['GET'])
def reports_totals_refresh(request):
    if request.method == 'GET':
        totals = {
            'total_reports': reports.objects.all().count(),
            'total_success_reports': reports.objects.all().filter(parse_success=True).count(),
            'total_failed_reports': reports.objects.all().filter(parse_success=False).count(),
        }
        return JsonResponse({"data":totals})
    
@api_view(['GET'])
def reports_refresh(request):
    if request.method == 'GET':
        allreports = reports.objects.all()
        if allreports:
            serializer = ReportsSerializer(allreports, many=True)
            allreports = serializer.data
        else:
            allreports = None
        return JsonResponse({"data":allreports})

def GlobalSearch(request):
    template_name = 'website/search.html'
    if request.method == 'POST':
        searched = request.POST.get('searched')
        foundscans = scans.objects.filter(scanName__icontains=searched)
        foundhosts = hosts.objects.filter(Q(main_address__icontains=searched) | Q(name__icontains=searched) | Q(hostnames__icontains=searched) | Q(description__icontains=searched))
        foundresourcegroups = resourcegroups.objects.filter(Q(name__icontains=searched) | Q(subnet__icontains=searched) | Q(description__icontains=searched))        
        return render(request, template_name, {'searched': searched, 'foundscans':foundscans, 'foundhosts':foundhosts, 'foundresourcegroups':foundresourcegroups})
    else:
        return render(request, template_name, {})

class ServiceDetailView(DetailView):
    model = services
    

#Chart API views
@api_view(['GET'])
def groups_piechart(request):
    if request.method == 'GET':        
        groupcount = resourcegroups.objects.all().count()
        color_codes = ['#' + ''.join([random.choice('0123456789ABCDEF') for _ in range(6)]) for _ in range(groupcount)]
        data = {
            'labels': [group.name for group in resourcegroups.objects.all() if group.hosts_count() > 0],
            'datasets': [{
                'data': [group.hosts_count() for group in resourcegroups.objects.all() if group.hosts_count() > 0],
                'backgroundColor': color_codes,
                'hoverBackgroundColor': [
                                        'rgba(255, 99, 132, 0.2)',
                                        'rgba(54, 162, 235, 0.2)',
                                        'rgba(255, 206, 86, 0.2)',
                                        'rgba(75, 192, 192, 0.2)',
                                        'rgba(153, 102, 255, 0.2)',
                                        'rgba(255, 159, 64, 0.2)'
                                    ]
            }]
        }
        options = {'responsive': False}
        return JsonResponse({'data': data, 'options': options})
    
@api_view(['GET'])
def scans_chart(request):
    groupcount = resourcegroups.objects.all().count()
    color_codes = ['#' + ''.join([random.choice('0123456789ABCDEF') for _ in range(6)]) for _ in range(groupcount)]
    data = {
    'labels': [group.name for group in resourcegroups.objects.all() if group.scans_count() > 0],
    'datasets': [{
      'data': [group.scans_count() for group in resourcegroups.objects.all() if group.scans_count() > 0],
      'backgroundColor': color_codes,
      'hoverBackgroundColor': ['#FF6384', '#36A2EB', '#FFCE56']
    }]
    }
    options = {'responsive': False}
    return JsonResponse({'data': data, 'options': options})

@api_view(['GET'])
def hosts_chart(request):
    if request.method == 'GET':        
        allhosts = hosts.objects.all().filter(status='up')
        hostcount = allhosts.count()
        color_codes = ['#' + ''.join([random.choice('0123456789ABCDEF') for _ in range(6)]) for _ in range(hostcount)]
        data = {
            'labels': [host.main_address for host in allhosts if host.num_open_ports() > 0],
            'datasets': [{
                'data': [host.num_open_ports() for host in allhosts if host.num_open_ports() > 0],
                'backgroundColor': color_codes,
                'borderWidth': 2
            }]
        }
        options = {
            'responsive': False,
            'legend': {
            'display': False
                    },
            'scales': {
                'yAxes': [{
                    'ticks': {
                        'stepSize': 1,
                        'beginAtZero': True,
                        'maxTicksLimit': 8
                    }
                }]
            }
        }
        return JsonResponse({'data': data, 'options': options})

@api_view(['GET'])
def reports_chart(request):
    if request.method == 'GET':
        #Number of changes in report over time per scan
        color_codes = ['#' + ''.join([random.choice('0123456789ABCDEF') for _ in range(6)]) for _ in range(scans.objects.all().count())]
        datasets = []
        for scan in scans.objects.all().filter(active=True).order_by('id'):
            reps = scan.reports_set.all().filter(parse_success=True).order_by('id')
            if reps:
                dataset = {
                    'label': scan.scanName,
                    'data': [rep.hosts_up for rep in reps if rep.hosts_up < 100],
                        'fill': False,
                        'borderColor': random.choice(color_codes), 
                        'borderWidth': 1,
                        'pointRadius': 3,
                        'pointHoverRadius': 5, 
                }
                datasets.append(dataset)
        allreports = reports.objects.all().filter(parse_success=True).order_by('-id')
        data = {
            'labels': [report.f_started_str() for report in allreports if report.parse_success],
            'datasets': datasets
        }
        options = {
            'responsive': False,
            'scales': {
                'yAxes': [{
                    'ticks': {
                        'stepSize': 1,
                        'beginAtZero': True,
                        'maxTicksLimit': 8
                    }
                }]
            }
        }
        return JsonResponse({'data': data, 'options': options})

@api_view(['GET'])
def dashboard_chart(request):
    if request.method == 'GET':
        colors = ['#FF6633', '#FFB399', '#FF33FF', '#FFFF99', '#00B3E6', '#E6B333', '#3366E6', '#999966', '#99FF99', '#B34D4D', '#80B300', '#809900', '#E6B3B3', '#6680B3', '#66991A']        
        colors_with_opacity = ['rgba(255, 102, 51, 0.6)', 'rgba(255, 179, 153, 0.6)', 'rgba(255, 51, 255, 0.6)','rgba(255, 255, 153, 0.6)', 'rgba(0, 179, 230, 0.6)', 'rgba(230, 179, 51, 0.6)', 'rgba(51, 102, 230, 0.6)', 'rgba(153, 153, 102, 0.6)', 'rgba(153, 255, 153, 0.6)','rgba(179, 77, 77, 0.6)', 'rgba(128, 179, 0, 0.6)', 'rgba(128, 153, 0, 0.6)','rgba(230, 179, 179, 0.6)', 'rgba(102, 128, 179, 0.6)', 'rgba(102, 153, 26, 0.6)']
        allreps = resourcegroups.objects.all()
        data = {
            'labels': [host.name for host in allreps if host.hostsup_count() > 0],
            'datasets': [{
                'data': [host.hostsup_count() for host in allreps if host.hostsup_count() > 0],
                'backgroundColor': colors,
                'hoverBackgroundColor': colors_with_opacity,
                'borderWidth': 2
            }]
        }
        options = {
            'responsive': True,
            'legend': {
            'display': False
                    },
            'scales': {
                'yAxes': [{
                    'ticks': {
                        'stepSize': 1,
                        'beginAtZero': True,
                        'maxTicksLimit': 8
                    }
                }]
            }
        }
        return JsonResponse({'data': data, 'options': options})
    
@api_view(['GET'])
def dashboard_scans(request):
    if request.method == 'GET':
        allscans = scans.objects.filter(active=True)
        serializer = ScansSerializer(allscans, many=True)
        return JsonResponse({"data":serializer.data})