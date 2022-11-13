from django.http import JsonResponse
from website.models import resourcegroups
from .serializers import ResourceSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

@api_view(['GET', 'POST'])
def Resource_list(request):
    if request.method == 'GET':
        resources = resourcegroups.objects.all()
        serializer = ResourceSerializer(resources, many=True)
        return JsonResponse({"resources":serializer.data})
    if request.method == 'POST':
        serializer = ResourceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
            