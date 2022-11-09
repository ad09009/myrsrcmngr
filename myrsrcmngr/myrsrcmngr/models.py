from django.db import models

class Resource(models.Model):
    add_date = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=600)
    def __str__(self):
        return self.name
    
class scans(models.Model):
    create_date = models.DateTimeField(auto_now_add=True)
    template_id = models.IntegerField()
    status = models.SmallIntegerField()
    parsed = models.BooleanField()
    path_to_xml = models.CharField(max_length=500)
    def __str__(self):
        return 'Scan at ' + self.call_date
    
class hosts(models.Model):
    main_address = models.CharField(max_length=50, blank=False)
    ipv4 = models.CharField(max_length=50)
    mac = models.CharField(max_length=50)
    vendor = models.CharField(max_length=100)
    ipv6 = models.CharField(max_length=50)
    status = models.CharField(max_length=50)
    hostnames = models.CharField(max_length=400)
    os_fingerprint = models.CharField(max_length=200)
    tcpsequence = models.CharField(max_length=50)
    ipsequence = models.CharField(max_length=50)
    uptime = models.CharField(max_length=50)
    lastboot = models.CharField(max_length=50)
    distance = models.IntegerField()