import shortuuid  # to generate short unique IDs
from django.shortcuts import render, redirect,get_object_or_404
from django.urls import reverse
from urllib3 import HTTPResponse
from .models import Agenda, CEOCurrentStatus, CEOStatus, CEOWaitingList, Reception, Token
from django.http import HttpResponse, JsonResponse
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

def generate_random_link(request):
    unique_url = shortuuid.uuid()  
    token = Token.objects.create(unique_url=unique_url)
    random_link = reverse('visitor_form', args=[unique_url])
    full_url = f"{request.build_absolute_uri(random_link)}"
    
    return redirect(full_url)


def visitor_form(request, unique_url):
    token = get_object_or_404(Token, unique_url=unique_url)
    
    # Check if the token has already been used
    if token.is_used:
        return render(request, 'error_page.html', {"message": "This link has already been used."})
    
    agendas = Agenda.objects.all()

    if request.method == 'POST':
        name = request.POST.get('name')
        agenda_id = request.POST.get('agenda')
        comment = request.POST.get('comment')

        agenda = get_object_or_404(Agenda,id=agenda_id)
        Reception.objects.create(name=name, agenda_name=agenda, comment=comment)
        
        # Mark the token as used
        token.is_used = True
        token.save()
        return redirect('success_page')

    return render(request, 'visitor_form.html',{'agendas':agendas})

def success_page(request):
    return render(request, 'success_page.html')


def pending_reception_count(request):
    if request.is_ajax():
        pending_count = Reception.objects.filter(status='pending').count()
        has_permission = request.user.is_superuser or request.user.has_perm('reception.view_reception')
        return JsonResponse({'pending_count': pending_count,'has_perm':has_permission})
    return JsonResponse({'error': 'Invalid request'}, status=400)


def pending_waiting_count(request):
    if request.is_ajax():
        pending_count = CEOWaitingList.objects.filter(status='pending').count()
        has_permission = request.user.is_superuser or request.user.has_perm('reception.view_reception')
        return JsonResponse({'pending_count': pending_count,'has_perm':has_permission})
    return JsonResponse({'error': 'Invalid request'}, status=400)


def ceo_appointment(request):
    # Query the CEO data
    ceo_data = CEOWaitingList.objects.all()
    selected_status = CEOCurrentStatus.objects.last() or ''

    # Pass the data to the template
    context = {
        'ceo_data': ceo_data,
        'selected_status': selected_status,
    }
    
    return render(request, 'ceo_appointment.html', context)



@csrf_exempt
def update_ceo_status(request):
    if request.method == "POST":
        data = json.loads(request.body)
        current_status = data.get("current_status")
        print(current_status)

        if current_status:
            # Save the selected status
            CEOCurrentStatus.objects.all().delete()
            CEOCurrentStatus.objects.create(current_status=current_status)
            return JsonResponse({"success": True})
        return JsonResponse({"success": False, "error": "Invalid status provided."})
    return JsonResponse({"success": False, "error": "Invalid request method."})