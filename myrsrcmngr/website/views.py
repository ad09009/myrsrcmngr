from django.shortcuts import render
from django.views import View
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.http import JsonResponse
from django.contrib.humanize.templatetags.humanize import naturaltime
from .serializers import ScansSerializer
from rest_framework.decorators import api_view
from .owner import OwnerCreateView, OwnerUpdateView, OwnerDeleteView

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

def about(request):
    return render(request, 'about.html', {})

#CRUD views for Scans

class ScanCreateView(OwnerCreateView):
    model = scans
    fields = ['scanName', 'ScanTemplate', 'ScanSchedule']
    # By convention:
    # template_name = "website/scans_form.html"

class ScanUpdateView(OwnerUpdateView):
    model = scans
    fields = ['scanName', 'ScanTemplate', 'ScanSchedule']
    # By convention:
    # template_name = "website/scans_form.html"

class ScanDeleteView(OwnerDeleteView):
    model = scans
    fields = ['scanName', 'ScanTemplate', 'ScanSchedule']
    # By convention:
    # template_name = "website/scans_confirm_delete.html"
    
class ScansListView(ListView):
    paginate_by = 5
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
            scanreturn['scan'] = 1
            scanreturn['scanname'] = mainscan.scanName
            if mainscan.active:
                scanreturn['active'] = 'On'
                if mainscan.status == 2:
                    scanreturn['status'] = mainscan.task_status
                    scanreturn['name'] = mainscan.task_name
                    scanreturn['etc'] = mainscan.task_etc
                    scanreturn['progress'] = mainscan.task_progress
                else:
                    scanreturn['status'] = mainscan.status
                    scanreturn['next_at'] = naturaltime(mainscan.next_execution_at)
            else:
                scanreturn['active'] = 'Off'
        else:
            scanreturn['scan'] = 0
        
        return JsonResponse(scanreturn, safe=False)
        
        
class ScanDetailView(DetailView):
    model = scans
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
    paginate_by = 5
    model = hosts
    # By convention:
    # template_name = "website/scans_list.html"

class HostDetailView(DetailView):
    model = hosts
    

#CRUD views for Groups

class ResourcegroupCreateView(OwnerCreateView):
    model = resourcegroups
    # By convention:
    # template_name = "website/hosts_form.html"

class ResourcegroupUpdateView(OwnerUpdateView):
    model = resourcegroups
    # By convention:
    # template_name = "website/scans_form.html"

class ResourcegroupDeleteView(OwnerDeleteView):
    model = resourcegroups
    # By convention:
    # template_name = "website/scans_confirm_delete.html"
    
class ResourcegroupsListView(ListView):
    paginate_by = 5
    model = resourcegroups
    # By convention:
    # template_name = "website/scans_list.html"

class ResourcegroupDetailView(DetailView):
    model = resourcegroups
    template_name = "website/resourcegroup_detail.html"

# List and Detail view for Reports

class ReportsListView(ListView):
    paginate_by = 5
    model = reports
    # By convention:
    # template_name = "website/scans_list.html"

class ReportDetailView(DetailView):
    model = reports
    
