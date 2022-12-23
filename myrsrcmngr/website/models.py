from django.db import models
from django.contrib.auth.models import User
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.utils.dateformat import DateFormat
from django.core.validators import MinValueValidator, MinLengthValidator

class resourcegroups(models.Model):
    add_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now = True, null=True)
    subnet = models.CharField("Subnet", max_length=100, blank=True, null=True, help_text = 'Only IPv4 addresses are supported. Indicate subnet in CIDR notation (e.g. 198.162.0.1/24)')
    name = models.CharField("Group Name",max_length=200, validators=[MinLengthValidator(3),])
    description = models.CharField("Description",max_length=600, blank=True, null=True)
    user = models.ForeignKey(User, null = True, on_delete=models.SET_NULL)
    ip_addresses = models.TextField("IP Addresses",blank=True, null=True)
    def __str__(self):
        return self.name
    
    def formatted_add_date(self):
        if self.add_date:
            return DateFormat(self.add_date).format("Y-m-d H:i:s")
        else:
            return None
        
    def formatted_updated_at(self):
        if self.updated_at:
            return DateFormat(self.updated_at).format("Y-m-d H:i:s")
        else:
            return None
    
    def scans_for_group(self):
        return self.scans_set.all()
    
    def hosts_for_group(self):
        return self.hosts_set.all()

    def scans_count(self):
        return self.scans_set.count()
    
    def hosts_count(self):
        return self.hosts_set.count()
    
    def active_scans_count(self):
        allscans = self.scans_set.all()
        if allscans:
            return allscans.filter(active=True).count()
        return 0
    
    def running_scans_count(self):
        allscans = self.scans_set.all()
        if allscans:
            return allscans.filter(active=True, status=2).count()
        return 0
    
    def hostsup_count(self):
        allhosts = self.hosts_set.all()
        if allhosts:
            return allhosts.filter(status="up").count()
        return 0
    
    def hostsdown_count(self):
        allhosts = self.hosts_set.all()
        if allhosts:
            return allhosts.filter(status="down").count()
        return 0
    
class scans(models.Model):
    create_date = models.DateTimeField("Date of Creation",auto_now_add=True)
    scanAuthor = models.ForeignKey(User, null = True, on_delete=models.SET_NULL)
    updated_at = models.DateTimeField("Date of Modification",auto_now = True, null=True)
    last_executed = models.DateTimeField("Last Executed at",blank=True, null=True)
    next_execution_at = models.DateTimeField("Next Execution at",null=True)
    scanName = models.CharField("Name",max_length=100, validators=[MinLengthValidator(3),])
    status = models.SmallIntegerField("Status",blank=True, null=True)
    #0 - self.DONE,
    #1 - self.READY,
    #2 - self.RUNNING,
    #3 - self.CANCELLED,
    #4 - self.FAILED
    task_name = models.CharField("Task Name",max_length=50, blank=True, null=True)
    task_status = models.CharField("Task Status",max_length=30, blank=True, null=True)
    task_etc = models.IntegerField(blank=True, null=True)
    task_progress = models.FloatField("Task Progress",blank=True, null=True)
    params = models.CharField("Parameters",max_length=200, blank=True, null=True)
    active = models.BooleanField("Make Active",default=False, blank=True, null=True)
    resourcegroup = models.ForeignKey(resourcegroups, verbose_name="Group Name", null=True, on_delete=models.SET_NULL)
    
    #scan_templates
    viens = '-oX -vvv --stats-every 1s --top-ports 100 -T2'
    divi = '--stats-every 1s --top-ports 100 -T3'
    tris = '--stats-every 1s --top-ports 100 -T4'
    SCAN_TEMPLATES = [
        (viens, '-oX -vvv --stats-every 1s --top-ports 100 -T2'),
        (divi, '--stats-every 1s --top-ports 100 -T3'),
        (tris, '--stats-every 1s --top-ports 100 -T4'),
    ]
    ScanTemplate = models.CharField( 
        "Scan Template",
        max_length=80,
        choices=SCAN_TEMPLATES,
        help_text = 'Indicate here the scan template you want to use. Free parameter entry is not supported yet.'
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
        "Scan Schedule",
        max_length=2,
        choices=SCAN_SCHEDULES,
        help_text = 'Indicate here how often would you like the scan to run.'
    )
    
    def __str__(self):
        return 'Scan ' + self.scanName + ' at ' + str(self.create_date)
    
    def get_data(self):
        return {
            
        }
    
    def formatted_status(self):
        # Return the string value of the status attribute
        if self.status == 0:
            return 'DONE'
        elif self.status == 1:
            return 'READY'
        elif self.status == 2:
            return 'RUNNING'
        elif self.status == 3:
            return 'CANCELLED'
        elif self.status == 4:
            return 'FAILED'
        else:
            return 'UNKNOWN'
    
    def formatted_schedule(self):
        # Return the string value of the status attribute
        if self.ScanSchedule == 'hh':
            return 'Every half-hour'
        elif self.ScanSchedule == 'h':
            return 'Every hour'
        elif self.ScanSchedule == 'd':
            return 'Every day'
        elif self.ScanSchedule == 'w':
            return 'Every week'
        else:
            return 'UNKNOWN'
    
    def formatted_active(self):
        if self.active:
            return "ON"
        else:
            return "OFF"
    
    def formatted_next_execution_at(self):
        if self.next_execution_at:
            return naturaltime(self.next_execution_at)
        else:
            return "None"
    
    def formatted_last_executed(self):
        if self.last_executed:
            return DateFormat(self.last_executed).format("jS F Y")
        else:
            return "Never"
    
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
    name = models.CharField(max_length=50, blank=True, null=True)
    description = models.CharField(max_length=200, blank=True, null=True)
    
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