from django.shortcuts import render
from .owner import OwnerCreateView, OwnerUpdateView, OwnerDeleteView
# Create your views here.
from .models import scans

def index(request):
    return render(request, 'index.html', {})

def about(request):
    return render(request, 'about.html', {})

class ScanCreateView(OwnerCreateView):
    model = scans
    fields = ['scanName', 'ScanTemplate', 'ScanSchedule']

    # By convention:
    # template_name = "receptes/scans_form.html"


class ScanUpdateView(OwnerUpdateView):
    model = scans
    fields = ['scanName', 'ScanTemplate', 'ScanSchedule']
    # By convention:
    # template_name = "receptes/scans_form.html"

class ScanDeleteView(OwnerDeleteView):
    model = scans
    fields = ['scanName', 'ScanTemplate', 'ScanSchedule']
    # By convention:
    # template_name = "receptes/scans_confirm_delete.html"