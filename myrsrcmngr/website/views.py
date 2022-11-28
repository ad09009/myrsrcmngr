from django.shortcuts import render
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from .owner import OwnerCreateView, OwnerUpdateView, OwnerDeleteView
# Create your views here.
from .models import scans, hosts, reports, resourcegroups

def index(request):
    return render(request, 'index.html', {})

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
    ordering = ['updated_at']
    # By convention:
    # template_name = "website/scans_list.html"

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
    

# List and Detail view for Reports

class ReportsListView(ListView):
    paginate_by = 5
    model = reports
    # By convention:
    # template_name = "website/scans_list.html"

class ReportDetailView(DetailView):
    model = reports