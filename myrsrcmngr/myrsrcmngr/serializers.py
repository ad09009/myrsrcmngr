from rest_framework import serializers
from website.models import resourcegroups

class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = resourcegroups
        fields = ['id', 'name', 'description', 'add_date']