from rest_framework import serializers
from ..models import Pattern, ScannedMessage

class PatternSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pattern
        fields = ['id', 'name', 'regex', 'description']

class ScannedMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScannedMessage
        fields = ['content', 'detected', 'matched_pattern', 'scanned_at']
