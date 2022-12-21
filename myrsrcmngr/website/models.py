from django.db import models
from django.contrib.auth.models import User

class resourcegroups(models.Model):
    add_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now = True, null=True)
    subnet = models.CharField(max_length=100, blank=True, null=True)
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=600, blank=True, null=True)
    user = models.ForeignKey(User, null = True, on_delete=models.SET_NULL)
    def __str__(self):
        return self.name
    
class scans(models.Model):
    create_date = models.DateTimeField(auto_now_add=True)
    scanAuthor = models.ForeignKey(User, null = True, on_delete=models.SET_NULL)
    updated_at = models.DateTimeField(auto_now = True, null=True)
    last_executed = models.DateTimeField(blank=True, null=True)
    next_execution_at = models.DateTimeField(null=True)
    scanName = models.CharField(max_length=100)
    status = models.SmallIntegerField(blank=True, null=True)
    #0 - self.DONE,
    #1 - self.READY,
    #2 - self.RUNNING,
    #3 - self.CANCELLED,
    #4 - self.FAILED
    task_name = models.CharField(max_length=50, blank=True, null=True)
    task_status = models.CharField(max_length=30, blank=True, null=True)
    task_etc = models.IntegerField(blank=True, null=True)
    task_progress = models.FloatField(blank=True, null=True)
    params = models.CharField(max_length=200, blank=True, null=True)
    active = models.BooleanField(blank=True, null=True)
    resourcegroup = models.ForeignKey(resourcegroups, null=True, on_delete=models.SET_NULL)
    
    #scan_templates
    viens = '-oX -vvv --stats-every 1s --top-ports 100 -T2'
    divi = '--stats-every 1s --top-ports 100 -T3'
    tris = '--stats-every 1s --top-ports 100 -T4'
    SCAN_TEMPLATES = [
        (viens, 'Pirmais variants'),
        (divi, 'Otrais variants'),
        (tris, 'Tresais variants'),
    ]
    ScanTemplate = models.CharField( 
        max_length=80,
        choices=SCAN_TEMPLATES
    )
    
    #scan_schedule
    halfhourly = 'hh'
    hourly = 'h'
    daily = 'd'
    weekly = 'w'
    SCAN_SCHEDULES = [
        (halfhourly, 'Every half hour'),
        (hourly, 'Every hour'),
        (daily, 'Every day'),
        (weekly, 'Every week'),
    ]
    ScanSchedule = models.CharField( 
        max_length=2,
        choices=SCAN_SCHEDULES
    )
    
    def __str__(self):
        return 'Scan ' + self.scanName + ' at ' + str(self.create_date)
    
    def get_data(self):
        return {
            
        }
    
class hosts(models.Model):
    main_address = models.CharField(max_length=50)
    ipv4 = models.CharField(max_length=50, blank=True, null=True)
    mac = models.CharField(max_length=50,blank=True, null=True)
    vendor = models.CharField(max_length=100, blank=True, null=True)
    ipv6 = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=50, blank=True, null=True)
    hostnames = models.CharField(max_length=400,blank=True, null=True)
    os_fingerprint = models.CharField(max_length=200, blank=True, null=True)
    tcpsequence = models.CharField(max_length=50, blank=True, null=True)
    ipsequence = models.CharField(max_length=50, blank=True, null=True)
    uptime = models.CharField(max_length=50, blank=True, null=True)
    lastboot = models.CharField(max_length=50, blank=True, null=True)
    distance = models.IntegerField(blank=True, null=True)
    resourcegroup = models.ForeignKey(resourcegroups, null = True, on_delete=models.SET_NULL)
    reports_belonging_to = models.ManyToManyField("reports", blank = True)
    is_removed = models.BooleanField(blank=True, null=True)
    is_added = models.BooleanField(blank=True, null=True)
    
class services(models.Model):
    port = models.IntegerField()
    state = models.CharField(max_length=50)
    protocol = models.CharField(max_length=50, blank=True, null=True)
    name_conc = models.CharField(max_length=200, blank=True, null=True)
    reason = models.CharField(max_length=100,blank=True, null=True)
    reason_ip = models.CharField(max_length=100,blank=True, null=True)
    reason_ttl = models.CharField(max_length=100, blank=True, null=True)
    service = models.CharField(max_length=150, blank=True, null=True)
    owner = models.CharField(max_length=100, blank=True, null=True)
    banner = models.CharField(max_length=400,blank=True, null=True)
    servicefp = models.CharField(max_length=200, blank=True, null=True)
    tunnel = models.CharField(max_length=100, blank=True, null=True)
    is_removed = models.BooleanField(blank=True, null=True)
    is_added = models.BooleanField(blank=True, null=True)
    host = models.ForeignKey(hosts, on_delete=models.CASCADE)
    reports_belonging_to = models.ManyToManyField("reports", blank = True)
    
class reports(models.Model):
    resourcegroup = models.ForeignKey(resourcegroups, null=True, on_delete=models.SET_NULL)
    prev_rep = models.IntegerField(blank=True, null=True)
    started_int = models.IntegerField(blank=True, null=True)
    endtime_int = models.IntegerField(blank=True, null=True)
    started_str = models.CharField(max_length=200, blank=True, null=True)
    endtime_str = models.CharField(max_length=200, blank=True, null=True)
    version = models.CharField(max_length=40, blank=True, null=True)
    scan_type = models.CharField(max_length=80, blank=True, null=True)
    num_services = models.IntegerField(blank=True, null=True)
    elapsed = models.IntegerField(blank=True, null=True)
    hosts_up = models.IntegerField(blank=True, null=True)
    hosts_down = models.IntegerField(blank=True, null=True)
    hosts_total = models.IntegerField(blank=True, null=True)
    summary = models.CharField(max_length=400,blank=True, null=True)
    full_cmndline = models.CharField(max_length=300, blank=True, null=True)
    path_to = models.CharField(max_length=400, blank=True, null=True)
    is_consistent = models.BooleanField(blank=True, null=True)
    scan = models.ForeignKey(scans, null=True, on_delete=models.SET_NULL)
    services_a_r = models.ManyToManyField(services, blank = True, through = "services_added_removed", through_fields=('cur_report','service'))
    hosts_a_r = models.ManyToManyField(hosts, blank = True, through = "hosts_added_removed", through_fields=('cur_report','host'))
    is_last = models.BooleanField(default=False)
    parse_success = models.BooleanField(default=True)
    get_latest_by = "-id"
    
class changes(models.Model):
    attribute = models.CharField(max_length=100, blank=True, null=True)
    cur_val = models.CharField(max_length=200, blank=True, null=True)
    prev_val = models.CharField(max_length=200, blank=True, null=True)
    status = models.CharField(max_length=70, blank=True, null=True)
    cur_report = models.ForeignKey(reports, on_delete=models.CASCADE)
    host = models.ForeignKey(hosts, blank=True, null=True, on_delete=models.SET_NULL)
    service = models.ForeignKey(services, blank=True, null=True, on_delete=models.SET_NULL)
    prev_rep = models.IntegerField(blank=True, null=True)

class services_added_removed(models.Model):
    status = models.CharField(max_length=20)
    prev_report = models.ForeignKey(reports, null=True, related_name="previous_report", on_delete=models.SET_NULL)
    cur_report = models.ForeignKey(reports, on_delete=models.CASCADE)
    service = models.ForeignKey(services, on_delete=models.CASCADE)
    
class hosts_added_removed(models.Model):
    status = models.CharField(max_length=20)
    prev_report = models.ForeignKey(reports, null=True, related_name="previous_report_hosts", on_delete=models.SET_NULL)
    cur_report = models.ForeignKey(reports, on_delete=models.CASCADE)
    host = models.ForeignKey(hosts, on_delete=models.CASCADE)