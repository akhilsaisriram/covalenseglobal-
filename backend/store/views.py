
from django.shortcuts import render
import tarfile
import io
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt  # Exempt CSRF protection
from django.views.decorators.http import require_http_methods
from .models import LogEntry  # Assuming the LogEntry model is in the same app
from .utils import process_tgz_file

@csrf_exempt
@require_http_methods(["POST"])
def process_tgz(request):
    """
    API endpoint to process an uploaded .tgz file, validate each log entry,
    and return the results of valid and invalid entries.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method is allowed'}, status=405)

    if 'file' not in request.FILES:
        return JsonResponse({'error': 'Please upload a .tgz file'}, status=400)
    
    tgz_file = request.FILES['file']
    
    try:
        # Process the TGZ file and collect results
        results = process_tgz_file(tgz_file)
        status_code = 201 if results['ignored_lines'] == [] else 206  # Partial success if no valid entries
        return JsonResponse(results, status=status_code)
        
    except Exception as e:
        return JsonResponse(
            {'error': 'Error processing TGZ file', 'details': str(e)},
            status=500
        )
    
from rest_framework import status
from .models import LogEntry
from .utils import validate_search_params
from .serializers import LogEntrySerializer
@csrf_exempt
def search_logs(request):
    # Extract query parameters
    searchstring = request.GET.get('searchstring', '')
    earliest_time = request.GET.get('EarliestTime', None)
    latest_time = request.GET.get('LatestTime', None)

    # Validate search parameters and catch validation errors
    try:
        filters = validate_search_params(searchstring, earliest_time, latest_time)
    except  Exception as e:
        return JsonResponse({'status': 'error', 'message': e.detail}, status=status.HTTP_400_BAD_REQUEST)

    # Query the database with validated filters
    log_entries = LogEntry.objects.filter(filters)
    
    # Check if any results are found
    if not log_entries.exists():
        return JsonResponse({'status': 'success', 'message': 'No results found'}, status=status.HTTP_200_OK)

    # Serialize the filtered log entries
    serializer = LogEntrySerializer(log_entries, many=True)
    return JsonResponse({'status': 'success','message':'results found','results': serializer.data}, status=status.HTTP_200_OK)