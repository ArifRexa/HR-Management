import json

from django.http import JsonResponse

# Create your views here.
from django.views.decorators.csrf import csrf_exempt

from employee.models import EmployeeActivity


@csrf_exempt
def change_status(request, *args, **kwargs):
    if request.method == 'POST':
        data = json.loads(request.body)
        use = request.user
        activity = EmployeeActivity.objects.filter(en)
    return JsonResponse({'status': 'success'})
