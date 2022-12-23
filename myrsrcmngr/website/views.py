from django.shortcuts import render
from django.views import View
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.http import JsonResponse
from django.contrib.humanize.templatetags.humanize import naturaltime
from .serializers import ScansSerializer, ReportsSerializer, ResourcegroupsSerializer, HostsSerializer
from rest_framework.decorators import api_view
from .owner import OwnerCreateView, OwnerUpdateView, OwnerDeleteView, GroupOwnerCreateView, GroupOwnerUpdateView, GroupOwnerDeleteView
from .forms import GroupsForm

# Create your views here.
from .models import scans, hosts, reports, resourcegroups

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

def dashboard(request):
    con = {}
    rreport = None
    report_changes = {}
    for rgroup in resourcegroups.objects.all().order_by('-updated_at'):
        
        try:
            rreport = rgroup.reports_set.latest('id')
            groupname = rgroup.name
            print(groupname)
            rchanges = rreport.changes_set.all().exclude(attribute='elapsed')
            print(rchanges)
            changes_count = rchanges.count()
            print(changes_count)
            if rchanges:
                print('here')
                report_changes['hosts_changed'] = 0
                print('here2')
                report_changes['hosts_added'] = 0
                report_changes['hosts_removed'] = 0
                report_changes['services_changed'] = 0
                report_changes['services_added'] = 0
                report_changes['services_removed'] = 0
                report_changes['hosts_up'] = None
                report_changes['hosts_down'] = None
                report_changes['hosts_total'] = None
                counter = 0
                print('rchanges')
                for change in rchanges:
                    print(change)
                    print(counter)
                    counter = counter + 1
                    if change.attribute == 'hosts_up':
                        print('hosts_up', change.cur_val, change.prev_val)
                        if change.prev_val is None:
                            print('prev_val is None')
                            change.prev_val = 0
                        report_changes['hosts_up'] = int(change.cur_val) - int(change.prev_val)
                        print('after hosts up')
                    elif change.attribute == 'hosts_down':
                        print('hosts_down')
                        if change.prev_val is None:
                            change.prev_val = 0
                        report_changes['hosts_down'] = int(change.cur_val) - int(change.prev_val)
                    elif change.attribute == 'hosts_total':
                        print('hosts_total')
                        if change.prev_val is None:
                            change.prev_val = 0
                        report_changes['hosts_total'] = int(change.cur_val) - int(change.prev_val)
                    elif change.status == 'CHANGED' and change.host is not None and change.service is None:
                        print('hosts_changed')
                        report_changes['hosts_changed'] = report_changes['hosts_changed'] + 1
                    elif change.status == 'ADDED' and change.host is not None and change.service is not None:
                        print('services_added')
                        report_changes['services_added'] = report_changes['services_added'] + 1
                    elif change.status == 'CHANGED' and change.host is not None and change.service is not None:
                        print('services_changed')
                        report_changes['services_changed'] = report_changes['services_changed'] + 1
                    elif change.status == 'REMOVED' and change.host is not None and change.service is not None:
                        print('services_removed')
                        report_changes['services_removed'] = report_changes['services_removed'] + 1
                    elif change.status == 'REMOVED' and change.host is not None and change.service is None:
                        print('hosts_removed')
                        report_changes['hosts_removed'] = report_changes['hosts_removed'] + 1
                    elif change.status == 'ADDED' and change.host is not None and change.service is None:
                        print('hosts_added')
                        report_changes['hosts_added'] = report_changes['hosts_added'] + 1
            print('report_changes')
            con[groupname] = {
                'report':rreport,
                'report_changes': report_changes,
                'changes':rchanges,
                'changes_count':changes_count,
            }
        except:
            print("no report")
            rreport = None
    context = {
        'con': con
    }
    for key, value in context['con'].items():
        print(key, value)
    print('something')
    return render(request, 'index.html', context)

def about(request):
    return render(request, 'about.html', {})

#CRUD views for Scans

class ScanCreateView(OwnerCreateView):
    model = scans
    fields = ['resourcegroup', 'scanName', 'ScanTemplate', 'ScanSchedule', 'active']
    # By convention:
    # template_name = "website/scans_form.html"

class ScanUpdateView(OwnerUpdateView):
    model = scans
    fields = ['resourcegroup', 'scanName', 'ScanTemplate', 'ScanSchedule', 'active']
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
        scan = scans.objects.get(pk=pk)
        scan.active = active
        scan.save()
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

class HostUpdateView(OwnerUpdateView):
    model = hosts
    # By convention:
    # template_name = "website/scans_form.html"

class HostDeleteView(OwnerDeleteView):
    model = hosts
    # By convention:
    # template_name = "website/scans_confirm_delete.html"
    
class HostsListView(ListView):
    model = hosts
    # By convention:
    # template_name = "website/scans_list.html"

class HostDetailView(DetailView):
    model = hosts
    

#CRUD views for Groups

class ResourcegroupCreateView(GroupOwnerCreateView):
    model = resourcegroups
    form_class = GroupsForm
    # By convention:
    # template_name = "website/hosts_form.html"

class ResourcegroupUpdateView(GroupOwnerUpdateView):
    model = resourcegroups
    form_class = GroupsForm
    # By convention:
    # template_name = "website/scans_form.html"

class ResourcegroupDeleteView(GroupOwnerDeleteView):
    model = resourcegroups
    # By convention:
    # template_name = "website/resourcegroups_confirm_delete.html"
    
class ResourcegroupsListView(ListView):
    model = resourcegroups
    # By convention:
    # template_name = "website/scans_list.html"

class ResourcegroupDetailView(DetailView):
    model = resourcegroups
    template_name = "website/resourcegroup_detail.html"

# List and Detail view for Reports

class ReportsListView(ListView):
    model = reports
    # By convention:
    # template_name = "website/scans_list.html"

class ReportDetailView(DetailView):
    model = reports
    

def GlobalSearch(request):
    template_name = 'website/search.html'
    if request.method == 'POST':
        searched = request.POST.get('searched')
        foundscans = scans.objects.filter(scanName__contains=searched)
        foundhosts = hosts.objects.filter(main_address__contains=searched)
        foundresourcegroups = resourcegroups.objects.filter(name__contains=searched)
        
        return render(request, template_name, {'searched': searched, 'foundscans':foundscans, 'foundhosts':foundhosts, 'foundresourcegroups':foundresourcegroups})
    else:
        return render(request, template_name, {})
