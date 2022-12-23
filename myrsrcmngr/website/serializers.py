from rest_framework import serializers
from .models import scans, reports, resourcegroups, hosts

class ScansSerializer(serializers.ModelSerializer):
    resourcegroup_id = serializers.SerializerMethodField()
    Flast_executed = serializers.SerializerMethodField()
    Fstatus = serializers.SerializerMethodField()
    Fnext_execution_at = serializers.SerializerMethodField()
    Factive = serializers.SerializerMethodField()
    Fresourcegroup = serializers.SerializerMethodField()
    class Meta:
        model = scans
        fields = ['id', 'Flast_executed', 'Fnext_execution_at', 'scanName', 'Fstatus', 'Factive', 'Fresourcegroup', 'resourcegroup_id']
    
    def get_resourcegroup_id(self, obj):
        return obj.resourcegroup.id
    
    def get_Fresourcegroup(self, obj):
        return obj.resourcegroup.name
    
    def get_Flast_executed(self, obj):
        return obj.formatted_last_executed()
    
    def get_Fnext_execution_at(self, obj):
        return obj.formatted_next_execution_at()
    
    def get_Fstatus(self, obj):
        return obj.formatted_status()
    
    def get_Factive(self, obj):
        return obj.formatted_active()
    
class ResourcegroupsSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    Fuser = serializers.SerializerMethodField()
    Fadd_date = serializers.SerializerMethodField()
    Fupdated_at = serializers.SerializerMethodField()
    class Meta:
        model = resourcegroups
        fields = ['id', 'Fadd_date', 'Fupdated_at', 'subnet', 'name', 'description', 'username', 'Fuser']
    
    def get_username(self, obj):
        return obj.user.username
    
    def get_Fuser(self, obj):
        return obj.user.profile.id
    
    def get_Fadd_date(self, obj):
        return obj.formatted_add_date()
    
    def get_Fupdated_at(self, obj):
        return obj.formatted_updated_at()
    
class ReportsSerializer(serializers.ModelSerializer):
    class Meta:
        model = reports
        fields = ['started_str', 'endtime_str', 'elapsed', 'num_services', 'hosts_up', 'hosts_down', 'hosts_total', 'id']
        
class HostsSerializer(serializers.ModelSerializer):
    num_of_services = serializers.SerializerMethodField()
    
    class Meta:
        model = hosts
        fields = ['id', 'main_address', 'hostnames', 'status', 'mac', 'os_fingerprint', 'num_of_services']      
    
    def get_num_of_services(self, obj):
        return obj.num_of_services()