from rest_framework import serializers
from .models import scans, reports

class ScansSerializer(serializers.ModelSerializer):
    class Meta:
        model = scans
        fields = ['last_executed', 'next_execution_at', 'scanName', 'status', 'active', 'resourcegroup']
        
class ReportsSerializer(serializers.ModelSerializer):
    class Meta:
        model = reports
        fields = ['started_str', 'endtime_str', 'elapsed', 'num_services', 'hosts_up', 'hosts_down', 'hosts_total', 'id']