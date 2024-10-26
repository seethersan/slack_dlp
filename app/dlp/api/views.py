from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from dlp.models import Pattern, ScannedMessage
from .serializers import PatternSerializer, ScannedMessageSerializer

# API to retrieve all patterns
@api_view(['GET'])
def get_patterns(request):
    patterns = Pattern.objects.all()
    serializer = PatternSerializer(patterns, many=True)
    return Response(serializer.data)

# API to save scanned message results
@api_view(['POST'])
def save_scan_result(request):
    serializer = ScannedMessageSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
