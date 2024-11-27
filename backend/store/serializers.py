# serializers.py

from rest_framework import serializers
from .models import LogEntry
import ipaddress

class LogEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = LogEntry
        fields = '__all__'

    def validate(self, data):
        errors = {}

        # Validate that `starttime` is before `endtime`
        if data['starttime'] > data['endtime']:
            errors['time_range'] = "Start time must be before end time."

        for field in ['srcaddr', 'dstaddr']:
            try:
                ipaddress.ip_address(data[field])
            except ValueError:
                errors[field] = f"{field} must be a valid IP address."

 

        # Check that bytes and packets are non-negative
        if data['bytes'] < 0:
            errors['bytes'] = "Bytes must be non-negative."
        if data['packets'] < 0:
            errors['packets'] = "Packets must be non-negative."

        # If there are errors, raise ValidationError with all collected errors
        if errors:
            raise serializers.ValidationError(errors)

        return data
