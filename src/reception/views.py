import shortuuid  # to generate short unique IDs
from django.shortcuts import render, redirect,get_object_or_404
from django.urls import reverse
from .models import Agenda, Reception, Token
from django.http import JsonResponse


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