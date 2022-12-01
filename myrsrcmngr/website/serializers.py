from rest_framework import serializers
from .models import scans

class ScansSerializer(serializers.ModelSerializer):
    class Meta:
        model = scans
        fields = ['last_executed', 'next_execution_at', 'scanName', 'status', 'active', 'resourcegroup']