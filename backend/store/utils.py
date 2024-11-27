# utils.py
import io
import tarfile
from .serializers import LogEntrySerializer
from .models import LogEntry  # Assuming LogEntry is a Django model for storing log entries
from django.db.models import Q
from rest_framework import serializers  # Add this import

import traceback



def process_tgz_file(tgz_file):
    """
    Processes a .tgz file containing log files, validates each log line,
    and returns structured results with errors and ignored lines if any.
    """
    results = {
        'files_processed': 0,
        'valid_entries': 0,
        'errors': [],
        'ignored_lines': []
    }
    log_entries = []  # List to hold LogEntry instances for bulk insert

    try:
        # Read the .tgz file content into memory
        file_content = io.BytesIO(tgz_file.read())
        
        # Open the TGZ file in memory
        with tarfile.open(fileobj=file_content, mode='r:gz') as tar:
            # Iterate through each file in the archive
            for member in tar.getmembers():
                if member.isfile():  # Process only files, not directories
                    try:
                        # Extract file content directly to memory
                        file_data = tar.extractfile(member)
                        if file_data:
                            try:
                                content = file_data.read().decode('utf-8')
                            except UnicodeDecodeError as e:
                                results['ignored_lines'].append({
                                    'filename': member.name,
                                    'error': f'UnicodeDecodeError: {str(e)}',
                                    'line': file_data.read().decode('utf-8', errors='ignore')  # Capture ignored content
                                })
                                continue  # Skip this file if decoding fails
                            
                            lines = content.splitlines()
                            
                            # Process the lines
                            for line in lines:
                                if not line.strip():  # Skip empty lines
                                    continue
                                parts = line.strip().split()
                                if len(parts) >= 14:  # Ensure we have all expected fields
                                    try:
                                        log_entry_data = {
                                            'serialno': int(parts[0]),
                                            'version': int(parts[1]),
                                            'account_id': int(parts[10]),
                                            'instance_id': parts[3],
                                            'srcaddr': parts[4],
                                            'dstaddr': parts[5],
                                            'srcport': int(parts[6]),
                                            'dstport': int(parts[7]),
                                            'protocol': int(parts[8]),
                                            'packets': int(parts[9]),
                                            'bytes': int(parts[9]),
                                            'starttime': int(parts[11]),
                                            'endtime': int(parts[12]),
                                            'action': parts[13],
                                            'log_status': parts[14] if len(parts) > 14 else 'UNKNOWN'
                                        }
                                        # Validate using the serializer
                                        serializer = LogEntrySerializer(data=log_entry_data)
                                        serializer.is_valid(raise_exception=True)
                                        log_entries.append(LogEntry(**log_entry_data))
                                    except ValidationError as e:
                                        results['errors'].append({
                                            'filename': member.name,
                                            'line': line,
                                            'error': str(e)
                                        })
                    except Exception as e:
                        results['errors'].append({
                            'filename': member.name,
                            'error': f'Error reading file: {str(e)}',
                            'traceback': traceback.format_exc()
                        })

            # Perform bulk insert if there are any valid log entries
            if log_entries:
                LogEntry.objects.bulk_create(log_entries)
                results['valid_entries'] = len(log_entries)

            # Update files processed count
            results['files_processed'] = len(tar.getmembers())

    except Exception as e:
        results['errors'].append({
            'error': f"Error processing TGZ file: {str(e)}",
            'traceback': traceback.format_exc()
        })
    print(results)
    return results

from django.db.models import Q
from rest_framework.exceptions import ValidationError
from .serializers import LogEntrySerializer

VALID_COLUMNS = ["account_id", "srcaddr", "dstaddr", "instance_id", "srcport", "dstport", "protocol", "packets", "bytes"]

def validate_search_params(searchstring, earliest_time, latest_time):
    """
    Validates search parameters and builds filters.
    Raises ValidationError with errors if any validation issues occur.
    Returns Q filters if all parameters are valid.
    """
    filters = Q()
    errors = {}

    # Validate searchstring and build filters
    if searchstring:
        search_params = searchstring.split(',')
        for param in search_params:
            if '=' not in param:
                errors.setdefault('search_params', []).append(f"Invalid format '{param}', expected 'key=value'")
                continue
            key, value = param.split('=', 1)
            if key not in VALID_COLUMNS:
                errors.setdefault('search_params', []).append(f"Invalid column name '{key}', must be one of {VALID_COLUMNS}")
            elif not value:
                errors.setdefault('search_params', []).append(f"No value provided for column '{key}'")
            else:
                # Attempt to convert values for integer-based fields
                try:
                    if key in ["account_id", "srcport", "dstport", "protocol", "packets", "bytes"]:
                        value = int(value)
                    filters &= Q(**{key: value})
                except ValueError:
                    errors.setdefault('search_params', []).append(f"Invalid value for '{key}', must be an integer.")

    # Validate earliest and latest times
    error_message=""
    try:
        if earliest_time:
            earliest_time = int(earliest_time)
            filters &= Q(starttime__gte=earliest_time)
        if latest_time:
            latest_time = int(latest_time)
            filters &= Q(endtime__lte=latest_time)
        # Check if earliest_time is after latest_time
        if earliest_time and latest_time and earliest_time > latest_time:

           errors.setdefault('time', []).append("Start time must be before end time.")
    except ValueError:
            errors.setdefault('time', []).append("Invalid time format. Please provide valid integer timestamps.")

    # Raise validation errors if any issues are found
    if errors:
        raise ValidationError(errors)

    return filters
